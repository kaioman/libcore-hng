import os
import math
import textwrap
from PIL import Image, ImageFont, ImageDraw
from dataclasses import dataclass
from typing import Optional
from libcore_hng.core.base_app_exception import AppBaseException
from libcore_hng.exceptions.file_exception import FontFileNotFoundError, ImageFileNotFoundError

class FontNotSetError(AppBaseException):
    """
    フォント未設定例外クラス
    
    - フォント設定を行っていない場合に発生する
    """

    def __init__(self):
        super().__init__(f"フォントが未設定です")

@dataclass(frozen=True)
class FaceCropResult:
    """
    顔切り抜き結果を表すデータクラス
    """

    image: Optional[Image.Image]
    """ 切り抜かれた顔の画像 """

    is_face: bool
    """ 顔が検出されたかどうか """

    score: Optional[float]
    """ 顔検出の信頼度スコア """

class ImageOps():
    """
    画像ロード専用のファクトリクラス

    このクラスは指定されたフォルダとファイル名から画像をロードし、
    ImageFile インスタンスを生成して返す
    """
    
    def __init__(self):
        """
        コンストラクタ
        """

        # オリジナルイメージパス
        self.org_image_path = ''
        
    def get_org_image_path(self):
        """
        現在保持しているオリジナル画像パスを返す。

        Returns
        -------
        str
            オリジナル画像のパス
        """
        
        # 戻り値を返す
        return self.org_image_path
    
    def load_image(self, org_folder_path: str, image_filename):
        """
        指定されたフォルダとファイル名から画像をロードし、
        ImageFile インスタンスを生成して返す。

        Parameters
        ----------
        org_folder_path : str
            画像ファイルが存在するフォルダパス
        image_filename : str
            画像ファイル名

        Returns
        -------
        ImageFile
            読み込んだ画像を操作するための ImageFile インスタンス

        Raises
        ------
        FileNotFoundErrorEx
            指定された画像ファイルが存在しない場合
        """
        
        # オリジナルイメージパスを設定する
        self.org_image_path = os.path.join(org_folder_path, image_filename)

        # 戻り値を返す
        return ImageFile(self.get_org_image_path())
    
class ImageFile:
    """
    イメージ操作用クラス
    
    Attributes
    ----------
    image_path : str
        読み込んだ画像ファイルのパス
    image : PIL.Image.Image
        現在操作対象の画像インスタンス
    _font : PIL.ImageFont.FreeTypeFont or None
        テキスト描画に使用するフォント
    """
    
    def __init__(self, image_path: str):
        """
        コンストラクタ

        Parameters
        ----------
        image_path : str
            読み込む画像ファイルのパス

        Raises
        ------
        FileNotFoundErrorEx
            指定された画像ファイルが存在しない場合
        """

        if not os.path.exists(image_path):
            raise ImageFileNotFoundError(image_path)
        self.image_path = image_path
        self.image = Image.open(image_path)
        self._font = None
        
    def resize(self, width: int):
        """
        画像をアスペクト比を維持したままリサイズする

        Parameters
        ----------
        width : int
            リサイズ後の幅（ピクセル）

        Returns
        -------
        ImageFile
            自身のインスタンス（メソッドチェーン可能）
        """

        new_size = (width, int(width * self.image.size[1] / self.image.size[0]))
        self.image = self.image.resize(new_size)
        return self

    def crop_face(self, padding: float = 0.2, min_detection_confidence: float = 0.5) -> FaceCropResult:
        """
        最大の顔を切り抜き、切り抜き後の顔検出結果を返す

        Parameters
        ----------
        padding : float, optional
            顔の周囲に追加するパディングの割合（デフォルトは 0.2）
        min_detection_confidence : float, optional
            顔検出の最小信頼度（デフォルトは 0.5）
        
        Returns
        -------
        FaceCropResult
            顔切り抜き結果を表すデータクラス
        """
        # paddingチェック
        if not math.isfinite(padding) or padding < 0:
            raise ValueError("paddingは 0 以上の有限値を指定してください")

        # min_detection_confidenceチェック
        if (
            not math.isfinite(min_detection_confidence)
            or not 0 <= min_detection_confidence <= 1
        ):
            raise ValueError(
                "min_detection_confidence は 0 以上 1 以下で"
            )

        # mediapipe と numpy のインポート
        try:
            import mediapipe as mp
            import numpy as np
        except ImportError as exc:
            raise ImportError(
                "crop_face には mediapipe と numpy が必要です"
            ) from exc

        # 画像を RGB に変換し、サイズを取得
        rgb_image = self.image.convert("RGB")
        image_width, image_height = rgb_image.size

        # mediapipe の FaceDetection を使用して顔を検出
        with mp.solutions.face_detection.FaceDetection(
            model_selection=1,
            min_detection_confidence=min_detection_confidence
        ) as detector:
            result = detector.process(np.asarray(rgb_image))
            detections = result.detections or []
            face_boxes = []

            # 検出された顔のバウンディングボックスを計算し、最大の顔を選択
            for detection in detections:

                # バウンディングボックスの座標を計算
                box = detection.location_data.relative_bounding_box
                # バウンディングボックスの座標を画像サイズに変換
                left = max(0, math.floor(box.xmin * image_width))
                top = max(0, math.floor(box.ymin * image_height))
                right = min(
                    image_width,
                    math.ceil((box.xmin + box.width) * image_width),
                )
                bottom = min(
                    image_height,
                    math.ceil((box.ymin + box.height) * image_height),
                )
                area = max(0, right - left) * max(0, bottom - top)
                if area:
                    face_boxes.append(
                        (area, detection, left, top, right, bottom)
                    )
                
            # 最大の顔が検出されなかった場合は None を返す
            if not face_boxes:
                return FaceCropResult(
                    image=None,
                    is_face=False,
                    score=None
                )

            # 最大の顔のバウンディングボックスを取得し、パディングを追加して切り抜く
            _, selected_detection, left, top, right, bottom = max(
                face_boxes, key=lambda face_box: face_box[0]
            )
            padding_x = round((right - left) * padding)
            padding_y = round((bottom - top) * padding)
            crop_box = (
                max(0, left - padding_x),
                max(0, top - padding_y),
                min(image_width, right + padding_x),
                min(image_height, bottom + padding_y),
            )
            cropped_image = rgb_image.crop(crop_box)

            # 切り抜いた画像で再度顔検出を行い、信頼度スコアを取得
            verified = detector.process(
                np.asarray(cropped_image)
            ).detections or []

            # 最大の顔が検出されなかった場合は None を返す
            if not verified:
                return FaceCropResult(image=None, is_face=False, score=None)

            # 選択された顔の信頼度スコアを取得
            score = float(selected_detection.score[0])
        
        # 切り抜いた画像を保持する
        self.image = cropped_image

        # 切り抜き後の顔検出結果を返す
        return FaceCropResult(
            image = self.image,
            is_face=True,
            score=score,
        )
    
    def set_font(self, font_path: str, size: int):        
        """
        テキスト描画用のフォントを設定する

        Parameters
        ----------
        font_path : str
            フォントファイルのパス
        size : int
            フォントサイズ

        Returns
        -------
        ImageFile
            自身のインスタンス（メソッドチェーン可能）

        Raises
        ------
        FontFileNotFoundErrorEx
            指定されたフォントファイルが存在しない場合
        """


        if not os.path.exists(font_path):
            raise FontFileNotFoundError(font_path)
        self._font = ImageFont.truetype(font_path, size)
        return self

    def insert_text(self, text: str, position: tuple, wrap_width = 14, color=(255,255,255)):
        """
        画像にテキストを描画する。

        Parameters
        ----------
        text : str
            描画するテキスト
        position : tuple
            テキスト描画開始位置 (x, y)
        wrap_width : int, optional
            テキストの折り返し幅（文字数単位）, デフォルトは 14
        color : tuple, optional
            テキストカラー (R, G, B), デフォルトは白 (255,255,255)

        Returns
        -------
        ImageFile
            自身のインスタンス（メソッドチェーン可能）

        Raises
        ------
        FontNotSetError
            フォントが設定されていない場合
        """

        # フォントが設定されていない場合
        if self._font is None:
            raise FontNotSetError
        
        # テキストの描画
        draw = ImageDraw.Draw(self.image)
        lines = textwrap.wrap(text, wrap_width)
        for i, line in enumerate(lines):
            # フォントサイズに応じてy座標を下げる
            y = position[1] + i * self._font.size
            # イメージにテキストを挿入する
            draw.text((position[1], y), line, font=self._font, fill=color)

        return self

    def save(self, output_folder: str, filename: str):
        """
        画像を指定したフォルダに保存する。

        Parameters
        ----------
        output_folder : str
            保存先フォルダ
        filename : str, optional
            保存時のファイル名。None の場合は元のファイル名を使用

        Returns
        -------
        str
            保存先のファイルパス
        """

        # 出力先ディレクトリ作成
        os.makedirs(output_folder, exist_ok=True)
        
        # ファイル名設定
        if filename is None:
            filename = os.path.basename(self.image_path)
        
        # 保存先パス設定
        save_path = os.path.join(output_folder, filename)
        
        # イメージを保存する
        self.image.save(save_path)
        
        # 保存先パスを返す
        return save_path