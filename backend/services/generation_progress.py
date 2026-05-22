"""In-memory generation progress tracker."""
import time
from typing import Optional
from pydantic import BaseModel


class GenerationProgress(BaseModel):
    stage: str = "idle"        # idle / analyzing / writing / images / formatting / done / error
    progress: int = 0          # 0-100
    message: str = ""
    started_at: Optional[float] = None
    finished_at: Optional[float] = None


_progress_store: dict[str, GenerationProgress] = {}

STAGES = [
    ("analyzing", "Analyzing your brand...", 10),
    ("writing", "Writing captions...", 35),
    ("images", "Searching for matching images...", 65),
    ("formatting", "Formatting posts...", 85),
    ("done", "Almost done!", 100),
]


def start_generation(user_id: str):
    _progress_store[user_id] = GenerationProgress(
        stage="analyzing",
        progress=5,
        message="Starting generation...",
        started_at=time.time(),
    )


def update_progress(user_id: str, stage: str, progress: int, message: str):
    if user_id in _progress_store:
        _progress_store[user_id].stage = stage
        _progress_store[user_id].progress = progress
        _progress_store[user_id].message = message


def finish_generation(user_id: str, error: bool = False):
    if user_id in _progress_store:
        _progress_store[user_id].stage = "error" if error else "done"
        _progress_store[user_id].progress = 100
        _progress_store[user_id].message = "Error during generation" if error else "Content ready!"
        _progress_store[user_id].finished_at = time.time()


def get_progress(user_id: str) -> GenerationProgress:
    return _progress_store.get(user_id, GenerationProgress())


def get_stage_progress(stage_index: int) -> tuple:
    """Get (stage_name, message, progress) for a given stage index."""
    if stage_index < len(STAGES):
        return STAGES[stage_index]
    return ("done", "Complete!", 100)
