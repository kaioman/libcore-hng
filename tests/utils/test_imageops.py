import sys
import pytest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any, List
from PIL import Image
from libcore_hng.utils.imageops import ImageFile

def _make_detection(
    xmin: float,
    ymin: float,
    width: float,
    height: float,
    score: float,
) -> Any:
    """
    検出結果を作成するためのヘルパー関数
    """
    box = SimpleNamespace(
        xmin=xmin,
        ymin=ymin,
        width=width,
        height=height,
    )
    return SimpleNamespace(
        location_data=SimpleNamespace(relative_bounding_box=box),
        score=[score],
    )

class _FakeDetector:
    """
    mediapipe.solutions.face_detection.FaceDetection のモッククラス
    """
    def __init__(self, results: List[List[Any]]) -> None:
        self._results = iter(results)

    def __enter__(self) -> "_FakeDetector":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any,traceback: Any) -> None:
        return None

    def process(self, image: Any) -> Any:
        """
        process メソッドは、次の検出結果を返す
        """
        return SimpleNamespace(detections=next(self._results))

def _install_fake_detector(monkeypatch: pytest.MonkeyPatch, results: List[List[Any]]) -> None:
    """
    mediapipe.solutions.face_detection.FaceDetection をモックに置き換える
    """
    # FakeDetector を作成し、指定された検出結果を返すようにする
    detector = _FakeDetector(results)

    # mediapipe と numpy モジュールを作成し、sys.modules に追加する
    mediapipe = ModuleType("mediapipe")
    mediapipe.solutions = SimpleNamespace(
        face_detection=SimpleNamespace(
            FaceDetection=lambda **kwargs: detector
        )
    )

    # numpy モジュールを作成し、asarray メソッドをモックする
    numpy = ModuleType("numpy")
    numpy.asarray = lambda image: image

    # sys.modules に mediapipe と numpy を追加する
    monkeypatch.setitem(sys.modules, "mediapipe", mediapipe)
    monkeypatch.setitem(sys.modules, "numpy", numpy)

def _create_image_file(tmp_path: Path) -> ImageFile:
    """
    画像ファイルを作成するためのヘルパー関数
    """
    # 100x100 の空の画像を作成し、tmp_path に保存する
    image_path = tmp_path / "source.png"
    Image.new("RGB", (100, 100)).save(image_path)
    return ImageFile(str(image_path))

def test_crop_face_return_score_for_largest_face(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch 
) -> None:
    """
    一番大きな顔のスコアを返すテスト
    """

    # 2つの顔を検出するようにモックを設定する
    smaller_face = _make_detection(0.7, 0.7, 0.1, 0.1, 0.99)
    largest_face = _make_detection(0.1, 0.1, 0.4, 0.4, 0.62)
    cropped_face = _make_detection(0.0, 0.0, 1.0, 1.0, 0.99)
    _install_fake_detector(
        monkeypatch,
        [[smaller_face, largest_face], [cropped_face]],
    )

    # 画像ファイルを作成し、crop_face メソッドを呼び出す
    result = _create_image_file(tmp_path).crop_face(padding=0)

    # 検出結果を検証する
    assert result.is_face is True
    assert result.score == 0.62
    assert result.image is not None
    assert result.image.size == (40, 40)

def test_crop_face_returns_none_when_cropped_image_has_no_face(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    顔が検出されない場合、crop_face メソッドは None を返すことを確認するテスト
    """
    # 1つの顔を検出するようにモックを設定するが、クロップ後の画像には顔がない
    detected_face = _make_detection(0.1, 0.1, 0.4, 0.4, 0.62)
    _install_fake_detector(monkeypatch, [[detected_face], []])
    image_file = _create_image_file(tmp_path)

    # crop_face メソッドを呼び出す
    result = image_file.crop_face(padding=0)

    # 検出結果を検証する
    assert result.image is None
    assert result.is_face is False
    assert result.score is None
    assert image_file.image.size == (100, 100)