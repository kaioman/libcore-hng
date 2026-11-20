import hashlib
import json
import sys
import pytest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Optional, Sequence
from PIL import Image
from libcore_hng.utils.face_similarity import FaceMatchStatus, FaceSimilarity, _FaceObservation

def _write_model_lock(tmp_path: Path) -> tuple[Path, Path, dict]:
    model_dir = tmp_path / "models"
    model_dir.mkdir()

    recognition_bytes = b"fake recognition model"
    detector_bytes = b"fake detector model"
    (model_dir / "glintr100.onnx").write_bytes(recognition_bytes)
    (model_dir / "yunet.onnx").write_bytes(detector_bytes)

    lock = {
        "default_model": "auraface_v1",
        "models": {
            "auraface_v1": {
                "recognition": {
                    "filename": "glintr100.onnx",
                    "revision": "recognition-revision",
                    "sha256": hashlib.sha256(recognition_bytes).hexdigest(),
                },
                "detector": {
                    "filename": "yunet.onnx",
                    "revision": "detector-revision",
                    "sha256": hashlib.sha256(detector_bytes).hexdigest(),
                    "options": {
                        "score_threshold": 0.9,
                        "nms_threshold": 0.3,
                    }
                },
                "thresholds": {
                    "match": 0.8,
                    "no_match": 0.3,
                },
                "quality": {
                    "min_face_size": 30,
                    "min_blur_variance": 10,
                    "max_landmark_asymmetry": 0.2,
                },
            }
        },
    }

    lock_file = tmp_path / "models.lock.json"
    lock_file.write_text(json.dumps(lock), encoding="utf-8")
    return lock_file, model_dir, lock

def _install_fake_runtime(monkeypatch: pytest.MonkeyPatch, cache_dir: Optional[Path] = None) -> None:
    cv2 = ModuleType("cv2")
    cv2.FaceDetectorYN = SimpleNamespace(
        create=lambda *args, **kwargs: object()
    )

    numpy = ModuleType("numpy")

    class FakeSession:
        def get_inputs(self):
            return [SimpleNamespace(shape=[1, 3, 112, 112], name="input")]

    onnxruntime = ModuleType("onnxruntime")
    onnxruntime.InferenceSession = lambda *args, **kwargs: FakeSession()

    monkeypatch.setitem(sys.modules, "cv2", cv2)
    monkeypatch.setitem(sys.modules, "numpy", numpy)
    monkeypatch.setitem(sys.modules, "onnxruntime", onnxruntime)

    if cache_dir is not None:
        platformdirs = ModuleType("platformdirs")
        platformdirs.user_cache_dir = lambda app_name: str(cache_dir)
        monkeypatch.setitem(sys.modules, "platformdirs", platformdirs)

def test_init_uses_default_cache_and_records_both_model_revisions(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    lock_file, model_dir, _ = _write_model_lock(tmp_path)
    cache_dir = tmp_path / "cache"
    cached_model_dir = cache_dir / "models"
    cached_model_dir.mkdir(parents=True)

    for filename in ("glintr100.onnx", "yunet.onnx"):
        (cached_model_dir / filename).write_bytes(
            (model_dir / filename).read_bytes()
        )

    _install_fake_runtime(monkeypatch, cache_dir)

    comparator = FaceSimilarity(lock_file=lock_file)

    assert comparator._model_dir == cached_model_dir
    assert comparator.model_revision == "recognition-revision"
    assert comparator.detector_revision == "detector-revision"

def test_init_rejects_model_with_mismatched_sha256(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch, 
) -> None:
    lock_file, model_dir, lock = _write_model_lock(tmp_path)
    lock["models"]["auraface_v1"]["recognition"]["sha256"] = "0" * 64
    lock_file.write_text(json.dumps(lock), encoding="utf-8")
    _install_fake_runtime(monkeypatch)

    with pytest.raises(ValueError, match="SHA-256"):
        FaceSimilarity(lock_file=lock_file, model_dir=model_dir)
    
def _make_comparator(
    observations: Sequence[Optional[_FaceObservation]],
    embeddings: Sequence[Sequence[float]] = (),
) -> FaceSimilarity:
    comparator = object.__new__(FaceSimilarity)
    comparator.model_name = "auraface_v1"
    comparator.model_revision = "recognition-revision"
    comparator.detector_revision = "detector-revision"
    comparator._match_threshold = 0.8
    comparator._no_match_threshold = 0.3
    comparator._np = SimpleNamespace(
        dot=lambda left, right: sum(a * b for a, b in zip(left, right))
    )

    observation_iter = iter(observations)
    embedding_iter = iter(embeddings)
    comparator._prepare_face = lambda image: next(observation_iter)
    comparator._embedding = lambda aligned_face: next(embedding_iter)
    return comparator

def _image() -> Image.Image:
    return Image.new("RGB", (32, 32), color="white")

def test_compare_returns_detection_failed_if_either_face_is_missing() -> None:
    comparator = _make_comparator(
        [
            _FaceObservation(aligned_face=object(), quality_reason=None),
            None,
        ]
    )

    result = comparator.compare(_image(), _image())

    assert result.status is FaceMatchStatus.DETECTION_FAILED
    assert result.score is None
    assert result.reason == "one_or_both_faces_not_detected"

@pytest.mark.parametrize(
    ("score", "expected_status"),
    [
        (0.8, FaceMatchStatus.MATCH),
        (0.3, FaceMatchStatus.NO_MATCH),
        (0.55, FaceMatchStatus.REVIEW),
    ],
)
def test_compare_applies_score_thresholds(score: float, expected_status: FaceMatchStatus) -> None:
    comparator = _make_comparator(
        [
            _FaceObservation(aligned_face=object(), quality_reason=None),
            _FaceObservation(aligned_face=object(), quality_reason=None),               
        ],
        embeddings=([score, 0.0], [1.0, 0.0]),
    )

    result = comparator.compare(_image(), _image())

    assert result.status is expected_status
    assert result.score == pytest.approx(score)
    assert result.model_revision == "recognition-revision"
    assert result.detector_revision == "detector-revision"

def test_compare_returns_review_without_score_for_low_quality_face() -> None:
    comparator = _make_comparator(
        [            
            _FaceObservation(
                aligned_face=None, 
                quality_reason="face_angle_too_large",
            ),
            _FaceObservation(
                aligned_face=object(), 
                quality_reason=None,
            )
        ]
    )

    result = comparator.compare(_image(), _image())

    assert result.status is FaceMatchStatus.REVIEW
    assert result.score is None
    assert result.reason == "face_angle_too_large"