import json
import hashlib
import math
import threading
from dataclasses import dataclass
from typing import Optional, Union
from enum import Enum
from pathlib import Path
from PIL import Image as PILImage
from PIL import ImageOps as PILImageOps

class FaceMatchStatus(str, Enum):
    """
    顔一致判定のステータスを表す列挙型
    """
    
    MATCH = "match"
    """ 一致 """

    REVIEW = "review"
    """ 判断保留 """

    NO_MATCH = "no_match"
    """ 不一致 """

    DETECTION_FAILED = "detection_failed"
    """ 検出失敗 """

@dataclass(frozen=True)
class FaceSimilarityResult:
    """
    顔類似度比較の結果を表すデータクラス
    """
    
    score: Optional[float]
    """ 類似度スコア。-1.0から1.0の範囲で、Noneの場合は比較できなかったことを示す """

    status: FaceMatchStatus
    """ 顔一致判定のステータス """

    model_name: str
    """ モデル名 """

    model_revision: str
    """ モデルのリビジョン """

    detector_revision: str
    """ 顔検出器のリビジョン """

    reason: Optional[str] = None
    """ 類似度比較が保留または失敗した理由。Noneの場合は理由なし """

@dataclass(frozen=True)
class _FaceObservation:
    """
    顔検出・位置合わせの結果を表すデータクラス
    """

    aligned_face: Optional[object]
    """ 位置合わせされた顔画像。Noneの場合は位置合わせに失敗したことを示す """

    quality_reason: Optional[object]
    """ 顔品質の理由。Noneの場合は品質に問題がないことを示す """

class FaceSimilarity:
    """
    YuNetで顔を検出・位置合わせし、ONNX顔認識モデルで類似度を計算する
    """

    def __init__(
        self, 
        *, 
        lock_file: Union[str, Path],
        model_dir: Optional[Union[str, Path]] = None,
        model_name: Optional[str] = None) -> None:
        """
        顔類似度比較のための初期化を行う

        Parameters
        ----------
        lock_file : Union[str, Path]
            モデルロックファイルのパス
        model_dir : Optional[Union[str, Path]]
            モデルディレクトリのパス
        model_name : Optional[str]
            モデル名
        """

        # 必要なライブラリのインポート
        try:
            import cv2
            import numpy as np
            import onnxruntime as ort
        except ImportError as exc:
            raise ImportError(
                "顔類似度機能にはopencv-python-headless, numpy, "
                "onnxruntimeが必要です"
            ) from exc

        # ライブラリをインスタンス変数に保存
        self._cv2 = cv2
        self._np = np
        self._ort = ort

        # モデルロックファイルの読み込み
        lock_path = Path(lock_file)
        if not lock_path.is_file():
            raise FileNotFoundError(f"モデルロックファイルがありません: {lock_path}")

        # モデルロックファイルの内容を読み込む
        with lock_path.open("r", encoding="utf-8") as file:
            lock = json.load(file)

        # モデル名の選択
        selected_name = model_name or lock.get("default_model")
        models = lock.get("models", {})
        if not selected_name or selected_name not in models:
            raise ValueError(f"未対応の顔認識モデルです: {selected_name}")

        # モデル設定の取得
        self.model_name = selected_name
        self._model_config = models[selected_name]
        self.model_revision = self._model_config["recognition"]["revision"]
        self.detector_revision = self._model_config["detector"]["revision"]

        # モデルディレクトリの設定
        if model_dir is None:
            try:
                from platformdirs import user_cache_dir
            except ImportError as exc:
                raise ImportError(
                    "model_dir省略時はplatformdirsが必要です"
                ) from exc
            model_dir = Path(user_cache_dir("libcore-hng")) / "models"
        self._model_dir = Path(model_dir)

        # モデルファイルの検証とパスの取得
        recognition_path = self._verified_model_path(
            self._model_config["recognition"]
        )
        detector_path = self._verified_model_path(
            self._model_config["detector"]
        )

        # 顔類似度比較の閾値と品質基準の設定
        thresholds = self._model_config.get("thresholds", {})
        self._match_threshold = self._required_number(
            thresholds.get("match"), "thresholds.match"
        )
        self._no_match_threshold = self._required_number(
            thresholds.get("no_match"), "thresholds.no_match"
        )
        if not -1 <= self._no_match_threshold < self._match_threshold <= 1:
            raise ValueError(
                "閾値は -1 <= no_match < match <= 1 を満たす必要があります"
            )

        # 品質基準の設定
        quality = self._model_config.get("quality", {})
        self._min_face_size = self._required_number(
            quality.get("min_face_size"), "quality.min_face_size"
        )
        self._min_blur_variance = self._required_number(
            quality.get("min_blur_variance"), "quality.min_blur_variance"
        )
        self._max_landmark_asymmetry = self._required_number(
            quality.get("max_landmark_asymmetry"), "quality.max_landmark_asymmetry"
        )
        if self._min_face_size <= 0 or self._min_blur_variance < 0:
            raise ValueError("品質基準の値が不正です")
        if self._max_landmark_asymmetry < 0:
            raise ValueError("角度品質基準の値は0以上で指定してください")

        # 顔検出器の初期化
        detector_config = self._model_config["detector"]
        detector_options = detector_config.get("options", {})
        self._detector = cv2.FaceDetectorYN.create(
            str(detector_path),
            "",
            (320, 320),
            float(self._required_number(
                detector_options.get("score_threshold"),
                "detector.options.score_threshold",
            )),
            float(self._required_number(
                detector_options.get("nms_threshold"),
                "detector.options.nms_threshold",
            )),
            5000,
        )
        self._detector_lock = threading.Lock()

        # 顔認識モデルの初期化
        self._session = ort.InferenceSession(
            str(recognition_path),
            providers=["CPUExecutionProvider"],
        )
        inputs = self._session.get_inputs()
        if len(inputs) != 1 or inputs[0].shape[1:] != [3, 112, 112]:
            raise ValueError(
                "AuraFaceモデルの入力が想定したNCHW (3, 112, 112) "
                "形式ではありません"
            )
        self._input_name = inputs[0].name

    @staticmethod
    def _required_number(value: object, key: str) -> float:
        """
        数値を確認し、floatに変換する
        
        Parameters
        ----------
        value : object
            確認する値
        key : str
            設定のキー

        Returns
        -------
        float
            変換された数値

        Raises
        ------
        ValueError
            値が不正な場合
        """

        # 値が数値であることを確認
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"models.lock.jsonに数値設定が必要です: {key}")        
        number = float(value)

        # 値が有限であることを確認
        if not math.isfinite(number):
            raise ValueError(f"設定値は有限値である必要があります: {key}")

        # 値を返す
        return number
    
    def _verified_model_path(self, entry: dict) -> Path:
        """
        モデルファイルのパスを検証し、有効なパスを返す
        
        Parameters
        ----------
        entry : dict
            モデルエントリ

        Returns
        -------
        Path
            有効なモデルファイルのパス

        Raises
        ------
        ValueError
            モデルファイルが見つからない場合
        """

        # モデルエントリから必要な情報を取得
        filename = entry.get("filename")
        revision = entry.get("revision")
        expected_hash = entry.get("sha256")

        # モデルファイルの存在とハッシュを検証
        if not filename or not revision:
            raise ValueError("モデルのfilenameとrevisionを設定してください")

        # SHA-256ハッシュの形式を検証
        if (
            not isinstance(expected_hash, str)
            or len(expected_hash) != 64
            or any(char not in "0123456789abcdefABCDEF" for char in expected_hash)   
        ):
            raise ValueError(
                f"有効なSHA-256がmodel.lock.jsonにありません: {filename}"
            )

        # モデルファイルのパスを構築し、存在を確認
        model_path = self._model_dir / filename
        if not model_path.is_file():
            raise FileNotFoundError(f"モデルファイルがありません: {model_path}")

        # モデルファイルのSHA-256ハッシュを計算し、期待値と比較
        digest = hashlib.sha256(model_path.read_bytes()).hexdigest()
        if digest.lower() != expected_hash.lower():
            raise ValueError(f"モデルのSHA-256が一致しません: {filename}")

        # モデルファイルのパスを返す
        return model_path

    @staticmethod
    def _load_rgb_image(
        image: Union[str, Path, PILImage.Image],
    ) -> PILImage.Image:
        """
        画像をRGB形式に変換する
        
        Parameters
        ----------
        image : Union[str, Path, PILImage.Image]
            処理する画像

        Returns
        -------
        PILImage.Image
            RGB形式の画像
        """

        # 画像がPIL.Image.Imageの場合はそのまま使用し、そうでない場合はファイルから読み込む
        if isinstance(image, PILImage.Image):
            return PILImageOps.exif_transpose(image).convert("RGB")

        # 画像がファイルパスの場合はPILで開き、RGB形式に変換して返す
        with PILImage.open(image) as opened:
            return PILImageOps.exif_transpose(opened).convert("RGB")

    def compare(
        self,
        image_a: Union[str, Path, PILImage.Image],
        image_b: Union[str, Path, PILImage.Image],
    ) -> FaceSimilarityResult:
        """
        2つの画像間の顔の類似度を比較する

        Parameters
        ----------
        image_a : Union[str, Path, PILImage.Image]
            比較する最初の画像
        image_b : Union[str, Path, PILImage.Image]
            比較する2番目の画像
        """ 

        # 画像をRGB形式で読み込む
        rgb_a = self._load_rgb_image(image_a)
        rgb_b = self._load_rgb_image(image_b)

        # 顔を検出・位置合わせし、類似度を計算する
        sample_a = self._prepare_face(rgb_a)
        sample_b = self._prepare_face(rgb_b)

        # 顔が検出されなかった場合の処理
        if sample_a is None or sample_b is None:
            return self._result(
                score=None,
                status=FaceMatchStatus.DETECTION_FAILED,
                reason="one_or_both_faces_not_detected",
            )

        # 顔品質の理由がある場合はレビュー状態で返す
        quality_reasons = [
            reason
            for reason in (sample_a.quality_reason, sample_b.quality_reason)
            if reason is not None
        ]
        if quality_reasons:
            return self._result(
                score=None,
                status=FaceMatchStatus.REVIEW,
                reason=",".join(quality_reasons),
            )

        # 顔位置合わせに失敗した場合の処理
        if sample_a.aligned_face is None or sample_b.aligned_face is None:
            return self._result(
                score=None,
                status=FaceMatchStatus.REVIEW,
                reason="face_alignment_failed",
            )

        # 顔特徴ベクトルを計算し、類似度スコアを算出する
        embedding_a = self._embedding(sample_a.aligned_face)
        embedding_b = self._embedding(sample_b.aligned_face)
        score = float(self._np.dot(embedding_a, embedding_b))
        score = max(-1.0, min(1.0, score))

        # 類似度スコアに基づいて一致判定を行う
        if score >= self._match_threshold:
            status = FaceMatchStatus.MATCH
        elif score <= self._no_match_threshold:
            status = FaceMatchStatus.NO_MATCH
        else:
            status = FaceMatchStatus.REVIEW

        # 結果を返す
        return self._result(
            score=score,
            status=status,
        )
    
    def _result(
        self,
        *,
        score: Optional[float],
        status:FaceMatchStatus,
        reason: Optional[str] = None
    ) -> FaceSimilarityResult:
        """
        類似度の結果を返す

        Parameters
        ----------
        score : Optional[float]
            類似度スコア
        status : FaceMatchStatus
            一致状態
        reason : Optional[str]
            理由

        Returns
        -------
        FaceSimilarityResult
            類似度の結果
        """

        # FaceSimilarityResultを作成して返す
        return FaceSimilarityResult(
            score=score,
            status=status,
            model_name=self.model_name,
            model_revision=self.model_revision,
            detector_revision=self.detector_revision,
            reason=reason,
        )

    def _prepare_face(
        self,
        rgb_image: PILImage.Image,
    ) -> Optional[_FaceObservation]:
        """
        顔を検出し、位置合わせする

        Parameters
        ----------
        rgb_image : PILImage.Image
            RGB形式の画像

        Returns
        -------
        Optional[_FaceObservation]
            顔検出・位置合わせの結果
        """

        # 画像をBGR形式に変換し、顔検出器で顔を検出する
        cv2 = self._cv2
        np = self._np
        bgr_image = cv2.cvtColor(np.asarray(rgb_image), cv2.COLOR_RGB2BGR)
        height, width = bgr_image.shape[:2]

        # 顔検出器の入力サイズを設定し、顔を検出する
        with self._detector_lock:
            self._detector.setInputSize((width, height))
            _, faces = self._detector.detect(bgr_image)

        # 顔が検出されなかった場合はNoneを返す
        if faces is None or len(faces) == 0:
            return None

        # 検出された顔の中で最も信頼度の高い顔を選択する
        face = max(faces, key=lambda row: max(0.0, row[2]) * max(0.0, row[3]))
        x, y, face_width, face_height = (int(round(v)) for v in face[:4])
        left = max(0, x)
        top = max(0, y)
        right = min(width, x + face_width)
        bottom = min(height, y + face_height)
        if right <= left or bottom <= top:
            return _FaceObservation(None, "invalid_face_box")

        # 顔の品質を評価する
        reasons = []
        if min(right - left, bottom - top) < self._min_face_size:
            return _FaceObservation(None, "face_too_small")

        # 顔領域を切り出し、グレースケールに変換してぼやけ具合を評価する
        face_region = bgr_image[top:bottom, left:right]
        gray_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        blur_variance = float(cv2.Laplacian(gray_face, cv2.CV_64F).var())
        if blur_variance < self._min_blur_variance:
            reasons.append("image_too_blurry")

        # 顔のランドマークを取得し、左右対称性を評価する
        landmarks = np.asarray(face[4:14], dtype=np.float32).reshape(5, 2)
        eye_span = abs(float(landmarks[1, 0] - landmarks[0, 0]))
        mouth_span = abs(float(landmarks[4, 0] - landmarks[3, 0]))
        if eye_span == 0 or mouth_span == 0:
            return _FaceObservation(None, "invalid_face_landmarks")

        # ランドマークの左右対称性を計算し、閾値を超える場合は理由に追加する
        nose_x = float(landmarks[2, 0])
        eye_midpoint_x = float((landmarks[0, 0] + landmarks[1, 0]) / 2)
        mouth_midpoint_x = float((landmarks[3, 0] + landmarks[4, 0]) / 2)
        landmark_asymmetry = max(
            abs(nose_x - eye_midpoint_x) / eye_span,
            abs(nose_x - mouth_midpoint_x) / mouth_span,
        )
        if landmark_asymmetry > self._max_landmark_asymmetry:
            reasons.append("face_angle_too_large")

        # 顔のランドマークを基準位置に合わせるためのアフィン変換を計算する
        reference = np.asarray(
            [
                [38.2946, 51.6963],
                [73.5318, 51.5014],
                [56.0252, 71.7366],
                [41.5493, 92.3655],
                [70.7299, 92.2041],
            ],
            dtype=np.float32,
        )
        affine, _ = cv2.estimateAffinePartial2D(
            landmarks,
            reference,
            method=cv2.LMEDS,
        )
        if affine is None:
            return _FaceObservation(None, "face_alignment_failed")

        # 顔を位置合わせし、_FaceObservationを返す 
        aligned = cv2.warpAffine(
            bgr_image,
            affine,
            (112, 112),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0),            
        )

        # 顔の品質理由を返す
        return _FaceObservation(
            aligned_face=aligned,
            quality_reason=",".join(reasons)
        )

    def _embedding(self, aligned_face: object):
        """
        位置合わせされた顔画像から特徴ベクトルを計算する

        Parameters
        ----------
        aligned_face : object
            位置合わせされた顔画像
        """

        # 顔画像をONNXモデルに入力し、特徴ベクトルを取得する
        cv2 = self._cv2
        np = self._np
        blob = cv2.dnn.blobFromImage(
            aligned_face,
            scalefactor=1.0 / 127.5,
            size=(112, 112),
            mean=(127.5, 127.5, 127.5),
            swapRB=False,
        )
        outputs = self._session.run(None, {self._input_name: blob})
        embedding = np.asarray(outputs[0], dtype=np.float32).reshape(-1)
        norm = float(np.linalg.norm(embedding))
        if not math.isfinite(norm) or norm == 0:
            raise RuntimeError("顔特徴ベクトルを正規化できません")
        
        # 正規化された特徴ベクトルを返す
        return embedding / norm