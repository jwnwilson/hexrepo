from ninja import Router

from .controllers.job_finder_controller import router as job_finder_router

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
