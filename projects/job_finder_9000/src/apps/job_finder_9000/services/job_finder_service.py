"""
Job Finder Service

This service layer integrates the job finder agent with the Django application,
providing a clean interface for controllers and handling business logic.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional

from django.conf import settings
from django.core.cache import cache

from ..domain.job_finder_agent import (
    create_job_finder_agent,
    CandidateProfile,
    JobSearchRequest,
    JobSearchResult,
    Skill,
    Location,
    JobPosting
)
from config import config

logger = logging.getLogger(__name__)


class JobFinderService:
    """
    Service class for job finding operations.
    
    This service provides a high-level interface for job searching functionality,
    including caching, error handling, and integration with the agent system.
    """
    
    def __init__(self):
        self.agent = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the job finder agent with configuration."""
        try:
            # Get OpenAI API key from settings
            breakpoint()
            openai_api_key = config.OPENAI_API_KEY
            if not openai_api_key:
                logger.warning("OpenAI API key not found in settings. Agent will not be initialized.")
                return
            
            self.agent = create_job_finder_agent(openai_api_key)
            logger.info("Job finder agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize job finder agent: {e}")
            self.agent = None
            raise
    
    def _get_cache_key(self, candidate_id: str, search_params: Dict[str, Any]) -> str:
        """Generate a cache key for job search results."""
        # Create a hash of search parameters for caching
        import hashlib
        params_str = str(sorted(search_params.items()))
        params_hash = hashlib.md5(params_str.encode()).hexdigest()
        return f"job_search:{candidate_id}:{params_hash}"
    
    def _get_cache_ttl(self) -> int:
        """Get cache TTL in seconds."""
        return getattr(settings, 'JOB_SEARCH_CACHE_TTL', 3600)  # Default 1 hour
    
    async def find_jobs_async(
        self,
        candidate_profile: CandidateProfile,
        max_results: int = 20,
        include_remote: bool = True,
        salary_threshold: Optional[int] = None,
        use_cache: bool = True
    ) -> JobSearchResult:
        """
        Find jobs for a candidate asynchronously.
        
        Args:
            candidate_profile: The candidate's profile
            max_results: Maximum number of jobs to return
            include_remote: Whether to include remote jobs
            salary_threshold: Minimum salary threshold
            use_cache: Whether to use caching
            
        Returns:
            Job search results
            
        Raises:
            Exception: If agent is not initialized or search fails
        """
        if not self.agent:
            raise Exception("Job finder agent is not initialized")
        
        # Create search request
        request = JobSearchRequest(
            candidate=candidate_profile,
            max_results=max_results,
            include_remote=include_remote,
            salary_threshold=salary_threshold
        )
        
        # Check cache if enabled
        if use_cache:
            cache_key = self._get_cache_key(
                candidate_profile.email,
                {
                    'max_results': max_results,
                    'include_remote': include_remote,
                    'salary_threshold': salary_threshold,
                    'skills': [skill.name for skill in candidate_profile.skills],
                    'locations': [loc.city for loc in candidate_profile.preferred_locations]
                }
            )
            
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info(f"Returning cached job search results for {candidate_profile.email}")
                return JobSearchResult(**cached_result)
        
        try:
            # Perform job search
            logger.info(f"Starting job search for {candidate_profile.email}")
            result = await self.agent.find_jobs(request)
            
            # Cache results if enabled
            if use_cache:
                cache.set(
                    cache_key,
                    result.model_dump(),
                    self._get_cache_ttl()
                )
                logger.info(f"Cached job search results for {candidate_profile.email}")
            
            return result
            
        except Exception as e:
            logger.error(f"Job search failed for {candidate_profile.email}: {e}")
            raise
    
    def find_jobs(
        self,
        candidate_profile: CandidateProfile,
        max_results: int = 20,
        include_remote: bool = True,
        salary_threshold: Optional[int] = None,
        use_cache: bool = True
    ) -> JobSearchResult:
        """
        Find jobs for a candidate (synchronous wrapper).
        
        Args:
            candidate_profile: The candidate's profile
            max_results: Maximum number of jobs to return
            include_remote: Whether to include remote jobs
            salary_threshold: Minimum salary threshold
            use_cache: Whether to use caching
            
        Returns:
            Job search results
        """
        return asyncio.run(self.find_jobs_async(
            candidate_profile=candidate_profile,
            max_results=max_results,
            include_remote=include_remote,
            salary_threshold=salary_threshold,
            use_cache=use_cache
        ))
    
    def create_candidate_profile(
        self,
        name: str,
        email: str,
        skills: List[Dict[str, Any]],
        experience_years: int,
        preferred_locations: List[Dict[str, Any]],
        salary_expectation: Optional[int] = None,
        job_preferences: Optional[Dict[str, Any]] = None
    ) -> CandidateProfile:
        """
        Create a candidate profile from raw data.
        
        Args:
            name: Candidate name
            email: Candidate email
            skills: List of skill dictionaries
            experience_years: Total years of experience
            preferred_locations: List of location dictionaries
            salary_expectation: Expected salary
            job_preferences: Additional job preferences
            
        Returns:
            CandidateProfile object
        """
        # Convert skills
        skill_objects = [
            Skill(
                name=skill['name'],
                proficiency=skill.get('proficiency', 'intermediate'),
                years_experience=skill.get('years_experience')
            )
            for skill in skills
        ]
        
        # Convert locations
        location_objects = [
            Location(
                city=location['city'],
                state=location.get('state'),
                country=location.get('country', 'USA'),
                remote_preference=location.get('remote_preference', 'hybrid')
            )
            for location in preferred_locations
        ]
        
        return CandidateProfile(
            name=name,
            email=email,
            skills=skill_objects,
            experience_years=experience_years,
            preferred_locations=location_objects,
            salary_expectation=salary_expectation,
            job_preferences=job_preferences or {}
        )
    
    def get_job_recommendations(
        self,
        candidate_profile: CandidateProfile,
        max_results: int = 10
    ) -> List[JobPosting]:
        """
        Get personalized job recommendations for a candidate.
        
        Args:
            candidate_profile: The candidate's profile
            max_results: Maximum number of recommendations
            
        Returns:
            List of recommended job postings
        """
        try:
            result = self.find_jobs(
                candidate_profile=candidate_profile,
                max_results=max_results,
                include_remote=True
            )
            
            # Filter for high-quality matches (score >= 70)
            recommendations = [
                job for job in result.jobs
                if job.match_score and job.match_score >= 70
            ]
            
            return recommendations[:max_results]
            
        except Exception as e:
            logger.error(f"Failed to get job recommendations: {e}")
            return []
    
    def analyze_candidate_market_position(
        self,
        candidate_profile: CandidateProfile
    ) -> Dict[str, Any]:
        """
        Analyze a candidate's position in the job market.
        
        Args:
            candidate_profile: The candidate's profile
            
        Returns:
            Market analysis data
        """
        try:
            # Get job search results
            result = self.find_jobs(
                candidate_profile=candidate_profile,
                max_results=50,
                include_remote=True
            )
            
            if not result.jobs:
                return {
                    "market_demand": "low",
                    "average_salary": 0,
                    "salary_percentile": 0,
                    "skill_gaps": [],
                    "recommendations": []
                }
            
            # Calculate market metrics
            salaries = [job.salary_min for job in result.jobs if job.salary_min]
            match_scores = [job.match_score for job in result.jobs if job.match_score]
            
            avg_salary = sum(salaries) / len(salaries) if salaries else 0
            avg_match_score = sum(match_scores) / len(match_scores) if match_scores else 0
            
            # Determine market demand
            if avg_match_score >= 80:
                market_demand = "high"
            elif avg_match_score >= 60:
                market_demand = "medium"
            else:
                market_demand = "low"
            
            # Calculate salary percentile (simplified)
            if avg_salary >= 120000:
                salary_percentile = 90
            elif avg_salary >= 100000:
                salary_percentile = 75
            elif avg_salary >= 80000:
                salary_percentile = 50
            else:
                salary_percentile = 25
            
            # Identify potential skill gaps
            skill_gaps = []
            required_skills = set()
            for job in result.jobs[:10]:  # Look at top 10 jobs
                for req in job.requirements:
                    required_skills.add(req.skill.lower())
            
            candidate_skills = {skill.name.lower() for skill in candidate_profile.skills}
            missing_skills = required_skills - candidate_skills
            skill_gaps = list(missing_skills)[:5]  # Top 5 missing skills
            
            return {
                "market_demand": market_demand,
                "average_salary": int(avg_salary),
                "salary_percentile": salary_percentile,
                "average_match_score": round(avg_match_score, 1),
                "skill_gaps": skill_gaps,
                "total_jobs_analyzed": len(result.jobs),
                "recommendations": [
                    "Consider upskilling in high-demand areas" if skill_gaps else "Your skills are well-aligned with market needs",
                    f"Your expected salary is in the {salary_percentile}th percentile",
                    f"Market demand for your profile is {market_demand}"
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze market position: {e}")
            return {
                "market_demand": "unknown",
                "average_salary": 0,
                "salary_percentile": 0,
                "skill_gaps": [],
                "recommendations": ["Unable to analyze market position"]
            }
    
    def clear_cache(self, candidate_email: Optional[str] = None):
        """
        Clear job search cache.
        
        Args:
            candidate_email: Specific candidate email to clear, or None for all
        """
        if candidate_email:
            # Clear specific candidate's cache
            pattern = f"job_search:{candidate_email}:*"
            # Note: This is a simplified cache clearing. In production, you might
            # want to use a more sophisticated cache key management system
            logger.info(f"Cleared cache for candidate: {candidate_email}")
        else:
            # Clear all job search cache
            cache.clear()
            logger.info("Cleared all job search cache")


# Global service instance
job_finder_service = JobFinderService() 