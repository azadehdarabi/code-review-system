from celery.utils.log import get_task_logger
import git
import os
from app.config import Settings
from celery import Celery

settings = Settings()

# Initialize Celery
celery_app = Celery('code_analysis', broker=settings.redis_url)
logger = get_task_logger(__name__)


@celery_app.task
def clone_repository(repo_url: str) -> str:
    job_id = celery_app.current_task.request.id
    repo_path = os.path.join(settings.repo_storage_path, job_id)

    try:
        logger.info(f"Starting repository clone: {repo_url} -> {repo_path}")
        os.makedirs(repo_path, exist_ok=True)

        git.Repo.clone_from(repo_url, repo_path, depth=None, multi_options=["--no-single-branch"])

        logger.info(f"Successfully cloned repository: {repo_path}")
        return job_id
    except Exception as e:
        logger.error(f"Cloning failed for {repo_url}: {str(e)}")
        raise
