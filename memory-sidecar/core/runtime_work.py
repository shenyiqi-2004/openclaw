from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.events import EventContext


REQUEST_TIME_WORK = "request-time"
POST_REQUEST_WORK = "post-request"
BACKGROUND_WORK = "background"
RECOVERY_WORK = "recovery"
MAINTENANCE_WORK = "maintenance"
MANUAL_WORK = "manual"


def classify_sidecar_work(event: "EventContext | None", *, worker_mode: bool) -> str:
    if event is None:
        return MANUAL_WORK
    if event.replayed:
        return RECOVERY_WORK
    if worker_mode:
        return BACKGROUND_WORK
    return POST_REQUEST_WORK
