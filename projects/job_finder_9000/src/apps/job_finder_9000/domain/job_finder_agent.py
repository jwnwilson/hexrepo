"""
Job Finder Agent System

This module implements a comprehensive job finding system using Pydantic AI agents.
The system orchestrates multiple specialized agents to find the highest paid and
most suitable jobs for candidates based on their skills and location preferences.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

import logfire
from pydantic import BaseModel, Field, ConfigDict
from pydantic_ai import Agent
from config import config

logger = logging.getLogger(__name__)


# =============================================================================
# Data Models
# =============================================================================

class Skill(BaseModel):
    """Represents a skill with proficiency level."""
    name: str = Field(..., description="Name of the skill")
    proficiency: str = Field(..., description="Proficiency level: beginner, intermediate, expert")
    years_experience: Optional[int] = Field(None, description="Years of experience with this skill")


class Location(BaseModel):
    """Represents a location preference."""
    city: str = Field(..., description="City name")
    state: Optional[str] = Field(None, description="State or province")
    country: str = Field(..., description="Country")
    remote_preference: str = Field("hybrid", description="Remote preference: on-site, hybrid, remote")


class CompanySearchResult(BaseModel):
    """Represents a company search result."""
    company_name: str = Field(..., description="Name of the company")
    location: str = Field(..., description="Company location")
    industry: str = Field(..., description="Company industry")
    hiring_status: str = Field(..., description="Current hiring status (active, limited, not hiring)")

class CompanySearchResponse(BaseModel):
    """Response model for company search."""
    companies: List[CompanySearchResult] = Field(..., description="List of companies to search for jobs")
    search_criteria: Dict[str, Any] = Field(..., description="Criteria used for the search")
    total_companies_found: int = Field(..., description="Total number of companies found")

class JobRequirement(BaseModel):
    """Represents a job requirement."""
    skill: str = Field(..., description="Required skill")
    level: str = Field(..., description="Required level: entry, mid, senior, lead")
    is_mandatory: bool = Field(True, description="Whether this is a mandatory requirement")

class JobPosting(BaseModel):
    """Represents a job posting."""
    title: str = Field(..., description="Job title")
    job_url: str = Field(..., description="URL to the job posting")
    match_score: Optional[float] = Field(None, description="Match score (0-100)")

class JobSearchResponse(BaseModel):
    """Response model for job search at a specific company."""
    jobs: List[JobPosting] = Field(..., description="List of active job postings found")
    company_name: str = Field(..., description="Name of the company searched")
    total_jobs_found: int = Field(..., description="Total number of jobs found for this company")
    search_sources: List[str] = Field(..., description="Sources that were searched")

class CandidateProfile(BaseModel):
    """Represents a candidate's profile."""
    name: str = Field(..., description="Candidate name")
    email: str = Field(..., description="Candidate email")
    skills: List[Skill] = Field(..., description="Candidate skills")
    experience_years: int = Field(..., description="Total years of experience")
    preferred_locations: List[Location] = Field(..., description="Preferred job locations")
    salary_expectation: Optional[int] = Field(None, description="Expected salary in USD")
    job_preferences: Dict[str, Any] = Field(default_factory=dict, description="Additional job preferences")


class JobSearchRequest(BaseModel):
    """Represents a job search request."""
    candidate: CandidateProfile = Field(..., description="Candidate profile")
    max_results: int = Field(5, description="Maximum number of jobs to return")
    include_remote: bool = Field(True, description="Include remote jobs")
    salary_threshold: Optional[int] = Field(None, description="Minimum salary threshold")


class JobSearchResult(BaseModel):
    """Represents the result of a job search."""
    jobs: List[JobPosting] = Field(..., description="Found job postings")
    total_found: int = Field(..., description="Total number of jobs found")
    search_duration: float = Field(..., description="Search duration in seconds")
    sources_searched: List[str] = Field(..., description="Job sources that were searched")
    summary: str = Field(..., description="Summary of the search results")


# =============================================================================
# Specialized Agents
# =============================================================================        

class CompanyFinderAgent:
    """Agent responsible for finding companies."""    
    def __init__(self, **kwargs):
        self.system_prompt = """You are an expert recruiter specializing in finding the highest paying companies closest to a candidate's preferred location.
You should prioritize companies based on:
- Geographic proximity to preferred locations
- Highest Salary and benefits
"""
        self.agent = Agent(
            name="CompanyFinderAgent",
            model=kwargs.get("model", config.DEFAULT_MODEL),
            output_type=CompanySearchResponse,
            system_prompt=self.system_prompt,
            retries=3
        )

    async def search_companies(self, company_agent_state: Dict[str, Any]) -> CompanySearchResponse:
        locations = company_agent_state.get("locations", [])
        keywords = company_agent_state.get("keywords", [])
        candidate = company_agent_state.get("candidate")
        include_remote = company_agent_state.get("include_remote", True)
        max_results = company_agent_state.get("max_results", 5)
        
        # Prepare context for LLM
        context = {
            "candidate_name": candidate.name if candidate else "Candidate",
            "candidate_skills": [skill.name for skill in candidate.skills] if candidate else keywords,
            "candidate_experience": candidate.experience_years if candidate else 0,
            "preferred_locations": locations,
            "salary_expectation": candidate.salary_expectation if candidate else None,
            "remote_preference": [loc.remote_preference for loc in candidate.preferred_locations] if candidate else ["hybrid"],
            "include_remote": include_remote,
            "max_companies": max_results
        }
        
        # Create prompt for LLM
        prompt = f"""
        Based on the following candidate profile and search criteria, search the internet and identify the best companies to search for job opportunities:

        Candidate Profile:
        - Skills: {', '.join(context['candidate_skills'])}
        - Years of Experience: {context['candidate_experience']}
        - Preferred Locations: {', '.join(context['preferred_locations'])}
        - Salary Expectation: {f"${context['salary_expectation']:,}" if context['salary_expectation'] else "Not specified"}

        Please identify up to {context['max_companies']} companies.
        """
        
        # Call LLM to get company recommendations
        try:
            with logfire.span(f"search_companies_prompt"):
                response = await self.agent.run(
                    prompt,

                )
                output = response.output
                return output
            
        except Exception as e:
            logger.error(f"Error searching for companies: {e}")
            raise

class JobFinderAgent:
    """Agent responsible for finding jobs."""    
    def __init__(self, **kwargs):
        self.system_prompt = """You are an expert recruiter specializing in finding active job postings from company websites and job boards. Your goal is to identify and extract detailed information about job opportunities that match the candidate's profile.

When searching for jobs, you should:

1. **Search Company Career Pages**: Look for active job postings on the company's official career website
2. **Check Job Boards**: Search major job boards like LinkedIn, Indeed, Glassdoor, and company-specific job sites
3. **Verify Job Status**: Ensure jobs are currently active and accepting applications
4. **Extract Complete Information**: Gather all relevant details including:
5. **Match Candidate Profile**: Prioritize jobs that align with candidate attributes
6. **Provide Direct Links**: Always include direct links to the actual job postings for easy application
7. **Validate Information**: Ensure all extracted information is accurate and up-to-date

Focus on finding high-quality, relevant job opportunities that would be attractive to the candidate based on their specific profile and preferences."""
        self.agent = Agent(
            name="JobFinderAgent",
            model=kwargs.get("model", config.DEFAULT_MODEL),
            output_type=JobSearchResponse,
            system_prompt=self.system_prompt,
            retries=3
        )

    async def get_active_jobs(self, company_agent_state: Dict[str, Any]) -> List[JobPosting]:
        companies = company_agent_state.get("companies", [])
        company_details = company_agent_state.get("company_details", [])
        candidate = company_agent_state.get("candidate")
        keywords = company_agent_state.get("keywords", [])
        max_results = company_agent_state.get("max_results", 50)
        
        if not companies:
            return []
        
        all_jobs = []
        
        for company_name in companies:
            # Find company details if available
            company_detail = next((c for c in company_details if c.company_name == company_name), None)
            
            # Prepare search context for this company
            search_context = {
                "company_name": company_name,
                "company_location": company_detail.location if company_detail else "Unknown",
                "company_industry": company_detail.industry if company_detail else "Technology",
                "candidate_skills": [skill.name for skill in candidate.skills] if candidate else keywords,
                "candidate_experience": candidate.experience_years if candidate else 0,
                "preferred_locations": [loc.city for loc in candidate.preferred_locations] if candidate else [],
                "salary_expectation": candidate.salary_expectation if candidate else None,
                "remote_preference": [loc.remote_preference for loc in candidate.preferred_locations] if candidate else ["hybrid"]
            }
            
            # Create search prompt for this company
            search_prompt = f"""
            Search for active job postings at {company_name} that match the following candidate profile:

            Company Information:
            - Name: {search_context['company_name']}
            - Location: {search_context['company_location']}
            - Industry: {search_context['company_industry']}

            Candidate Profile:
            - Skills: {', '.join(search_context['candidate_skills'])}
            - Years of Experience: {search_context['candidate_experience']}
            - Preferred Locations: {', '.join(search_context['preferred_locations'])}
            - Salary Expectation: {f"${search_context['salary_expectation']:,}" if search_context['salary_expectation'] else "Not specified"}
            - Remote Preference: {', '.join(search_context['remote_preference'])}

            Please search the following sources for active job postings:
            1. {company_name}'s official career website
            2. LinkedIn job postings for {company_name}
            3. Indeed job postings for {company_name}
            4. Glassdoor job postings for {company_name}
            5. Other relevant job boards

            Return up to 5 most relevant job postings for this company, along with the search sources used.
            """
            
            try:
                with logfire.span(f"get_active_jobs_prompt"):
                    # Call LLM to search for jobs at this company
                    response: JobSearchResponse = await self.agent.run(
                        search_prompt,
                    )
                    output = response.output
                    # Add jobs from this company to the total list
                    all_jobs.extend(output.jobs)
            except Exception as e:
                logger.error(f"Error searching for jobs at {company_name}: {e}")
                raise
        
        # Limit total results and sort by match score
        all_jobs.sort(key=lambda x: x.match_score or 0, reverse=True)
        return all_jobs[:max_results]

    async def filter_jobs(self, company_agent_state: Dict[str, Any]) -> List[JobPosting]:
        """
        Filter jobs based on candidate skills, salary expectations, and preferences.
        """
        active_jobs = company_agent_state.get("active_jobs", [])
        candidate = company_agent_state.get("candidate")
        
        if not candidate:
            return active_jobs
        
        # Sort by match score (highest first)
        active_jobs.sort(key=lambda x: x.match_score or 0, reverse=True)
        
        return active_jobs


# =============================================================================
# Main Orchestrator Agent
# =============================================================================

class JobFinderOrchestrator:
    """
    Main orchestrator agent that coordinates all specialized agents to find
    the best job opportunities for candidates.
    """
    
    
    def __init__(self, model: str | None = None, model_settings: dict | None = None):
        self.model_settings = model_settings or {}
        self.model = model or config.DEFAULT_MODEL
        self.company_finder: Agent = CompanyFinderAgent(model=model)
        self.job_finder: Agent = JobFinderAgent(model=model)

    async def find_jobs(self, request: JobSearchRequest) -> JobSearchResult:
        """
        Main method to find jobs for a candidate.
        
        Args:
            request: Job search request with candidate profile
            
        Returns:
            Job search results with ranked job postings
        """
        with logfire.span(f"find_jobs"):
            start_time = datetime.now()
            
            # Extract search parameters
            candidate = request.candidate
            max_results = request.max_results
            include_remote = request.include_remote
            
            # Generate search keywords from skills
            keywords = [skill.name for skill in candidate.skills]
            
            # Get preferred locations
            locations = [loc.city for loc in candidate.preferred_locations]
            if not locations:
                company_agent_state["include_remote"] = include_remote

            company_agent_state = {
                "locations": locations,
                "include_remote": include_remote,
                "keywords": keywords,
                "companies": [],
                "active_jobs": [],
                "filtered_jobs": [],
                "max_results": max_results,
                "candidate": candidate,
            }
            
            # Search for high paying companies in the preferred locations
            company_search_response = await self.company_finder.search_companies(company_agent_state)
            company_agent_state["companies"] = [company.company_name for company in company_search_response.companies]
            company_agent_state["company_details"] = company_search_response.companies

            # Get active jobs from the high paying companies
            company_agent_state["active_jobs"] = await self.job_finder.get_active_jobs(company_agent_state)

            # Filter jobs by candidate skills and salary expectation
            company_agent_state["filtered_jobs"] = filtered_jobs = await self.job_finder.filter_jobs(company_agent_state)
            
            # Calculate search duration
            end_time = datetime.now()
            search_duration = (end_time - start_time).total_seconds()
            
            # Generate summary
            summary = self._generate_search_summary(filtered_jobs, candidate, search_duration)
            
            return JobSearchResult(
                jobs=filtered_jobs,
                total_found=len(filtered_jobs),
                search_duration=search_duration,
                sources_searched=company_agent_state["companies"],
                summary=summary
            )
    
    def _generate_search_summary(self, jobs: List[JobPosting], candidate: CandidateProfile, duration: float) -> str:
        """Generate a summary of the job search results."""
        if not jobs:
            return f"No suitable jobs found for {candidate.name} in {duration:.2f} seconds."
        
        top_jobs = jobs[:3]
        top_companies = [job.title for job in top_jobs]
        
        summary = f"""
        Found {len(jobs)} suitable jobs for {candidate.name} in {duration:.2f} seconds.
        
        Top opportunities:
        - Top Jobs: {', '.join(top_companies)}
        
        Best matches:
        """
        
        for i, job in enumerate(top_jobs, 1):
            summary += f"{i}. {job.title} at {job.title} ({job.match_score}% match)\n"
        
        return summary.strip()


# =============================================================================
# Factory Functions
# =============================================================================

def create_job_finder_agent(openai_api_key: str) -> JobFinderOrchestrator:
    """
    Create and configure a job finder orchestrator agent.
    
    Args:
        openai_api_key: OpenAI API key for the agent
        
    Returns:
        Configured job finder agent
    """
    # Set the OpenAI API key as an environment variable
    import os
    os.environ["OPENAI_API_KEY"] = openai_api_key
    
    return JobFinderOrchestrator(
        model=config.DEFAULT_MODEL,
        model_settings={
            "temperature": 0.1,
            "max_tokens": 4000
        }
    )


# =============================================================================
# Usage Example
# =============================================================================

async def example_usage():
    """Example of how to use the job finder agent system."""
    
    # Create candidate profile
    candidate = CandidateProfile(
        name="John Doe",
        email="john.doe@example.com",
        skills=[
            Skill(name="Python", proficiency="expert", years_experience=5),
            Skill(name="JavaScript", proficiency="intermediate", years_experience=3),
            Skill(name="AWS", proficiency="intermediate", years_experience=2),
        ],
        experience_years=5,
        preferred_locations=[
            Location(city="San Francisco", state="CA", country="USA", remote_preference="hybrid"),
            Location(city="New York", state="NY", country="USA", remote_preference="hybrid"),
        ],
        salary_expectation=120000,
        job_preferences={"industry": "tech", "company_size": "startup"}
    )
    
    # Create search request
    request = JobSearchRequest(
        candidate=candidate,
        max_results=5,
        include_remote=True,
        salary_threshold=80000
    )
    
    # Create agent (you'll need to provide your OpenAI API key)
    # agent = create_job_finder_agent("your-openai-api-key")
    
    # Find jobs
    # result = await agent.find_jobs(request)
    
    # Print results
    # print(result.summary)
    # for job in result.jobs[:5]:
    #     print(f"{job.title} at {job.company} - {job.match_score}% match")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
