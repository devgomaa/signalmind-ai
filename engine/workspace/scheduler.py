"""
engine/workspace/scheduler.py
==============================
Sprint 6: APScheduler — كل workspace له جدول تشغيل مستقل.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from engine.utils.logger import get_logger

logger = get_logger("Scheduler")

_scheduler = None


def get_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler(timezone="UTC")
        _scheduler.start()
        logger.info("Scheduler started")
    return _scheduler


def run_workspace_pipeline(workspace_id: int):
    """تشغيل الـ pipeline لـ workspace محدد."""
    logger.info(f"Scheduled run for workspace: {workspace_id}")
    try:
        from engine.pipelines.workspace_pipeline import WorkspacePipeline
        WorkspacePipeline(workspace_id).run()
    except Exception as e:
        logger.error(f"Scheduled pipeline failed (ws:{workspace_id}): {e}")


def schedule_workspace(workspace_id: int, hours: int = 6):
    """إضافة أو تحديث جدول workspace."""
    scheduler  = get_scheduler()
    job_id     = f"workspace_{workspace_id}"

    # إزالة الجدول القديم لو موجود
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)

    scheduler.add_job(
        func=run_workspace_pipeline,
        trigger=IntervalTrigger(hours=hours),
        args=[workspace_id],
        id=job_id,
        name=f"Pipeline — Workspace {workspace_id}",
        replace_existing=True,
    )
    logger.info(f"Scheduled workspace {workspace_id} every {hours}h")


def unschedule_workspace(workspace_id: int):
    """إيقاف جدول workspace."""
    scheduler = get_scheduler()
    job_id    = f"workspace_{workspace_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        logger.info(f"Unscheduled workspace {workspace_id}")


def get_all_jobs() -> list:
    """قائمة كل الـ jobs النشطة."""
    scheduler = get_scheduler()
    jobs = []
    for job in scheduler.get_jobs():
        next_run = job.next_run_time.isoformat() if job.next_run_time else None
        jobs.append({
            "id":       job.id,
            "name":     job.name,
            "next_run": next_run,
        })
    return jobs


def init_all_workspace_schedules():
    """عند بدء الـ app — يُفعّل جداول كل الـ workspaces."""
    try:
        from engine.auth.auth_manager import get_auth
        workspaces = get_auth().get_all_workspaces()
        for ws in workspaces:
            schedule_workspace(ws["id"], ws.get("schedule_hours", 6))
        logger.info(f"Initialized {len(workspaces)} workspace schedules")
    except Exception as e:
        logger.error(f"Failed to init schedules: {e}")
