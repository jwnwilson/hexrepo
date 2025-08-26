"""
Job Finder API Controllers

This module contains the API controllers for the job finder application.
These controllers handle HTTP requests and responses using Django Ninja.
"""

import logging
from typing import Dict, Any
from datetime import datetime

from django.conf import settings
import logfire
from ninja import Router
from ninja.errors import HttpError

from ..services.job_finder_service import job_finder_service
from .job_finder_schemas import (
    JobSearchRequestSchema,
    JobSearchSuccessSchema,
    JobRecommendationsRequestSchema,
    RecommendationsSuccessSchema,
    MarketAnalysisRequestSchema,
    MarketAnalysisSuccessSchema,
    HealthCheckSchema,
    CacheClearSchema,
    ErrorSchema,
    ValidationErrorSchema
)

logger = logging.getLogger(__name__)

# Create router
router = Router(tags=["job-finder"])


@router.post("/search", response={200: JobSearchSuccessSchema, 400: ErrorSchema, 500: ErrorSchema})
def search_jobs(request, payload: JobSearchRequestSchema):
    """
    Search for jobs based on candidate profile.
    
    This endpoint searches for jobs across multiple sources and returns
    the best matches based on skills, location, and salary preferences.
    """
    with logfire.span(f"search_jobs_request"):
        try:
            # Create candidate profile from request
            candidate_profile = job_finder_service.create_candidate_profile(
                name=payload.name,
                email=payload.email,
                skills=[skill.dict() for skill in payload.skills],
                experience_years=payload.experience_years,
                preferred_locations=[loc.dict() for loc in payload.preferred_locations],
                salary_expectation=payload.salary_expectation,
                job_preferences=payload.job_preferences
            )
            
            # Perform job search
            result = job_finder_service.find_jobs(
                candidate_profile=candidate_profile,
                max_results=payload.max_results,
                include_remote=payload.include_remote,
                salary_threshold=payload.salary_threshold,
                use_cache=payload.use_cache
            )
            
            # Convert result to schema
            jobs_data = []
            for job in result.jobs:
                job_data = {
                    "title": job.title,
                    "job_url": job.job_url,
                    "match_score": job.match_score,
                }
                jobs_data.append(job_data)
            
            search_result_data = {
                "jobs": jobs_data,
                "total_found": result.total_found,
                "search_duration": result.search_duration,
                "sources_searched": result.sources_searched,
                "summary": result.summary
            }
            
            return 200, JobSearchSuccessSchema(
                success=True,
                message="Job search completed successfully",
                data=search_result_data
            )
            
        except ValueError as e:
            logger.error(f"Validation error in job search: {e}")
            return 400, ErrorSchema(
                error="Validation Error",
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error in job search: {e}")
            return 500, ErrorSchema(
                error="Internal Server Error",
                detail="An error occurred while searching for jobs"
            )


@router.post("/recommendations", response={200: RecommendationsSuccessSchema, 400: ErrorSchema, 500: ErrorSchema})
def get_job_recommendations(request, payload: JobRecommendationsRequestSchema):
    """
    Get personalized job recommendations for a candidate.
    
    This endpoint provides high-quality job recommendations based on
    the candidate's profile and preferences.
    """
    try:
        # Create candidate profile from request
        candidate_profile = job_finder_service.create_candidate_profile(
            name=payload.name,
            email=payload.email,
            skills=[skill.dict() for skill in payload.skills],
            experience_years=payload.experience_years,
            preferred_locations=[loc.dict() for loc in payload.preferred_locations],
            salary_expectation=payload.salary_expectation
        )
        
        # Get recommendations
        recommendations = job_finder_service.get_job_recommendations(
            candidate_profile=candidate_profile,
            max_results=payload.max_results
        )
        
        # Convert recommendations to schema
        recommendations_data = []
        total_score = 0
        
        for job in recommendations:
            job_data = {
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "salary_range": job.salary_range,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "description": job.description,
                "requirements": [
                    {
                        "skill": req.skill,
                        "level": req.level,
                        "is_mandatory": req.is_mandatory
                    }
                    for req in job.requirements
                ],
                "benefits": job.benefits,
                "job_url": job.job_url,
                "posted_date": job.posted_date,
                "match_score": job.match_score,
                "source": job.source
            }
            recommendations_data.append(job_data)
            if job.match_score:
                total_score += job.match_score
        
        avg_match_score = total_score / len(recommendations) if recommendations else 0
        
        summary = f"Found {len(recommendations)} high-quality job recommendations with an average match score of {avg_match_score:.1f}%"
        
        return 200, RecommendationsSuccessSchema(
            success=True,
            message="Job recommendations generated successfully",
            data={
                "recommendations": recommendations_data,
                "total_recommendations": len(recommendations),
                "average_match_score": round(avg_match_score, 2),
                "summary": summary
            }
        )
        
    except ValueError as e:
        logger.error(f"Validation error in recommendations: {e}")
        return 400, ErrorSchema(
            error="Validation Error",
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in recommendations: {e}")
        return 500, ErrorSchema(
            error="Internal Server Error",
            detail="An error occurred while generating recommendations"
        )


@router.post("/market-analysis", response={200: MarketAnalysisSuccessSchema, 400: ErrorSchema, 500: ErrorSchema})
def analyze_market_position(request, payload: MarketAnalysisRequestSchema):
    """
    Analyze a candidate's position in the job market.
    
    This endpoint provides insights into market demand, salary expectations,
    and skill gaps for the candidate's profile.
    """
    try:
        # Create candidate profile from request
        candidate_profile = job_finder_service.create_candidate_profile(
            name=payload.name,
            email=payload.email,
            skills=[skill.dict() for skill in payload.skills],
            experience_years=payload.experience_years,
            preferred_locations=[loc.dict() for loc in payload.preferred_locations],
            salary_expectation=payload.salary_expectation
        )
        
        # Perform market analysis
        analysis = job_finder_service.analyze_candidate_market_position(candidate_profile)
        
        return 200, MarketAnalysisSuccessSchema(
            success=True,
            message="Market analysis completed successfully",
            data=analysis
        )
        
    except ValueError as e:
        logger.error(f"Validation error in market analysis: {e}")
        return 400, ErrorSchema(
            error="Validation Error",
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in market analysis: {e}")
        return 500, ErrorSchema(
            error="Internal Server Error",
            detail="An error occurred while analyzing market position"
        )


@router.get("/health", response={200: HealthCheckSchema})
def health_check(request):
    """
    Check the health status of the job finder service.
    
    This endpoint provides information about the service status,
    including agent availability and API version.
    """
    try:
        # Check agent status
        agent_status = "healthy" if job_finder_service.agent else "unavailable"
        
        return 200, HealthCheckSchema(
            status="healthy",
            timestamp=datetime.now(),
            version=getattr(settings, 'APP_VERSION', '1.0.0'),
            agent_status=agent_status
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return 200, HealthCheckSchema(
            status="unhealthy",
            timestamp=datetime.now(),
            version=getattr(settings, 'APP_VERSION', '1.0.0'),
            agent_status="error"
        )


@router.post("/cache/clear", response={200: CacheClearSchema})
def clear_cache(request, candidate_email: str = None):
    """
    Clear job search cache.
    
    This endpoint clears cached job search results, either for a specific
    candidate or for all candidates.
    """
    try:
        job_finder_service.clear_cache(candidate_email)
        
        message = f"Cache cleared for candidate: {candidate_email}" if candidate_email else "All cache cleared"
        
        return 200, CacheClearSchema(
            success=True,
            message=message,
            cleared_entries=None  # Could be enhanced to return actual count
        )
        
    except Exception as e:
        logger.error(f"Cache clearing failed: {e}")
        return 200, CacheClearSchema(
            success=False,
            message=f"Failed to clear cache: {str(e)}",
            cleared_entries=0
        )


@router.get("/skills", response={200: Dict[str, Any]})
def get_available_skills(request):
    """
    Get list of available skills for job searching.
    
    This endpoint returns a curated list of skills that can be used
    for job searching and profile creation.
    """
    try:
        # This could be enhanced to pull from a database or external API
        skills = {
            "programming_languages": [
                "Python", "JavaScript", "Java", "C++", "C#", "Go", "Rust", "TypeScript",
                "PHP", "Ruby", "Swift", "Kotlin", "Scala", "R", "MATLAB"
            ],
            "frameworks": [
                "Django", "Flask", "FastAPI", "React", "Vue.js", "Angular", "Spring",
                "Express.js", "Laravel", "Ruby on Rails", "ASP.NET", "TensorFlow", "PyTorch"
            ],
            "databases": [
                "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra",
                "DynamoDB", "SQLite", "Oracle", "SQL Server"
            ],
            "cloud_platforms": [
                "AWS", "Azure", "Google Cloud", "Heroku", "DigitalOcean", "Vercel",
                "Netlify", "Firebase", "Kubernetes", "Docker"
            ],
            "tools": [
                "Git", "Jenkins", "GitLab CI", "GitHub Actions", "Jira", "Confluence",
                "Slack", "Docker", "Terraform", "Ansible", "Prometheus", "Grafana"
            ],
            "methodologies": [
                "Agile", "Scrum", "Kanban", "DevOps", "CI/CD", "TDD", "BDD",
                "Microservices", "REST API", "GraphQL", "Event-Driven Architecture"
            ]
        }
        
        return 200, {
            "success": True,
            "message": "Available skills retrieved successfully",
            "data": skills
        }
        
    except Exception as e:
        logger.error(f"Error retrieving skills: {e}")
        return 500, {
            "success": False,
            "message": "Failed to retrieve available skills",
            "error": str(e)
        }


@router.get("/locations", response={200: Dict[str, Any]})
def get_popular_locations(request):
    """
    Get list of popular job locations.
    
    This endpoint returns a curated list of popular job locations
    that can be used for job searching.
    """
    try:
        # This could be enhanced to pull from a database or external API
        locations = {
            "united_states": {
                "tech_hubs": [
                    {"city": "San Francisco", "state": "CA", "country": "USA"},
                    {"city": "New York", "state": "NY", "country": "USA"},
                    {"city": "Seattle", "state": "WA", "country": "USA"},
                    {"city": "Austin", "state": "TX", "country": "USA"},
                    {"city": "Boston", "state": "MA", "country": "USA"},
                    {"city": "Denver", "state": "CO", "country": "USA"},
                    {"city": "Chicago", "state": "IL", "country": "USA"},
                    {"city": "Los Angeles", "state": "CA", "country": "USA"}
                ],
                "emerging_markets": [
                    {"city": "Nashville", "state": "TN", "country": "USA"},
                    {"city": "Raleigh", "state": "NC", "country": "USA"},
                    {"city": "Salt Lake City", "state": "UT", "country": "USA"},
                    {"city": "Portland", "state": "OR", "country": "USA"}
                ]
            },
            "international": {
                "canada": [
                    {"city": "Toronto", "state": "ON", "country": "Canada"},
                    {"city": "Vancouver", "state": "BC", "country": "Canada"},
                    {"city": "Montreal", "state": "QC", "country": "Canada"}
                ],
                "europe": [
                    {"city": "London", "state": None, "country": "UK"},
                    {"city": "Berlin", "state": None, "country": "Germany"},
                    {"city": "Amsterdam", "state": None, "country": "Netherlands"},
                    {"city": "Paris", "state": None, "country": "France"},
                    {"city": "Stockholm", "state": None, "country": "Sweden"}
                ],
                "asia": [
                    {"city": "Singapore", "state": None, "country": "Singapore"},
                    {"city": "Tokyo", "state": None, "country": "Japan"},
                    {"city": "Seoul", "state": None, "country": "South Korea"},
                    {"city": "Bangalore", "state": None, "country": "India"}
                ]
            },
            "remote_options": [
                {"city": "Remote", "state": None, "country": "Any"},
                {"city": "Hybrid", "state": None, "country": "Any"}
            ]
        }
        
        return 200, {
            "success": True,
            "message": "Popular locations retrieved successfully",
            "data": locations
        }
        
    except Exception as e:
        logger.error(f"Error retrieving locations: {e}")
        return 500, {
            "success": False,
            "message": "Failed to retrieve popular locations",
            "error": str(e)
        } 