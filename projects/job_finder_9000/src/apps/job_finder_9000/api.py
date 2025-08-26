from ninja import Router
import logfire
from config import config
from .controllers.job_finder_controller import router as job_finder_router

# configure logfire
logfire.configure(token=config.LOGFIRE_WRITE_TOKEN)
logfire.instrument_pydantic_ai()

# Main router
router = Router(tags=["Job_finder_9000"])

# Include job finder routes
router.add_router("/jobs/", job_finder_router)


@router.get("/")
def get_job_finder_9000(request):
    """Root endpoint for the job finder application."""
    return {
        "message": "Welcome to Job Finder 9000!",
        "version": "1.0.0",
        "endpoints": {
            "job_search": "/jobs/search",
            "recommendations": "/jobs/recommendations", 
            "market_analysis": "/jobs/market-analysis",
            "health_check": "/jobs/health",
            "skills": "/jobs/skills",
            "locations": "/jobs/locations"
        }
    }
