from celery import Celery
import git
import os
from .config import Settings

settings = Settings()

# Initialize Celery
celery_app = Celery('code_analysis', broker=settings.redis_url)

@celery_app.task
def clone_repository(repo_url: str) -> str:
    """
    Clone a GitHub repository to local storage.
    Returns the job_id which is the Celery task ID.
    """
    try:
        # Create a unique directory for this repo
        job_id = celery_app.current_task.request.id
        repo_path = os.path.join(settings.repo_storage_path, job_id)
        
        # Ensure the directory exists
        os.makedirs(repo_path, exist_ok=True)
        
        # Clone the repository
        git.Repo.clone_from(repo_url, repo_path)
        
        return job_id
    except Exception as e:
        # Log the error and re-raise
        celery_app.logger.error(f"Failed to clone repository: {str(e)}")
        raise 