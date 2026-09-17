import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.core.config import settings
from backend.scheduler.sweep import run_the_sweep

logger = logging.getLogger("assistiq.scheduler")

scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler:
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler()
    return scheduler


def start_scheduler() -> None:
    """
    Initializes and starts the in-process APScheduler.
    Follows SRS §3.5 & AGENTS_AssistIQ.md §5-§6 (single in-process sweep, no external workers).
    """
    sched = get_scheduler()
    if not sched.running:
        interval_minutes = max(1, settings.SWEEP_INTERVAL_MINUTES)
        sched.add_job(
            run_the_sweep,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id="the_sweep_job",
            name="AssistIQ The Sweep (SLA, Risk, Escalation)",
            replace_existing=True,
            coalesce=True,
            max_instances=1,
        )
        sched.start()
        logger.info(f"In-process APScheduler started. 'The Sweep' running every {interval_minutes} minute(s).")


def stop_scheduler() -> None:
    """
    Gracefully shuts down the in-process scheduler.
    """
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("In-process APScheduler stopped.")
        scheduler = None
