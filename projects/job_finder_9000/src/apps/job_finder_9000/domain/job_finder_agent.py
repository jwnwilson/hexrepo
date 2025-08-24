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
    company_size: str = Field(..., description="Company size (startup, mid-size, enterprise)")
    average_salary: Optional[int] = Field(None, description="Average salary for the role in this company")
    hiring_status: str = Field(..., description="Current hiring status (active, limited, not hiring)")
    remote_friendly: bool = Field(False, description="Whether the company supports remote work")
    reasoning: str = Field(..., description="Reason why this company was selected")


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
    company: str = Field(..., description="Company name")
    location: str = Field(..., description="Job location")
    salary_range: Optional[str] = Field(None, description="Salary range if available")
    salary_min: Optional[int] = Field(None, description="Minimum salary in USD")
    salary_max: Optional[int] = Field(None, description="Maximum salary in USD")
    description: str = Field(..., description="Job description")
    requirements: List[JobRequirement] = Field(default_factory=list, description="Job requirements")
    benefits: List[str] = Field(default_factory=list, description="Job benefits")
    job_url: str = Field(..., description="URL to the job posting")
    posted_date: Optional[datetime] = Field(None, description="When the job was posted")
    match_score: Optional[float] = Field(None, description="Match score (0-100)")
    source: str = Field(..., description="Source of the job posting")

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
    max_results: int = Field(50, description="Maximum number of jobs to return")
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

class CompanyFinderAgent(Agent):
    """Agent responsible for finding companies."""
    
    model_config = ConfigDict(extra="forbid")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.output_type = CompanySearchResponse
        self.system_prompt = """You are an expert recruiter specializing in finding the highest paying companies closest to a candidate's preferred location. Your goal is to identify companies that:

1. Are located in or near the candidate's preferred locations
2. Pay above-market salaries for the candidate's skill set
3. Are actively hiring for positions matching the candidate's experience
4. Offer the work arrangement (remote/hybrid/on-site) the candidate prefers

You should prioritize companies based on:
- Salary competitiveness and benefits
- Geographic proximity to preferred locations
- Company reputation and stability
- Growth potential and career advancement opportunities
- Work-life balance and company culture

When analyzing companies, consider:
- Industry trends and market demand
- Company size and funding status
- Recent hiring activity and job postings
- Employee reviews and satisfaction ratings
- Compensation transparency and equity offerings

Return a comprehensive list of companies that would be most attractive to the candidate based on their skills, experience, location preferences, and salary expectations."""

    async def search_companies(self, company_agent_state: Dict[str, Any]) -> CompanySearchResponse:
        """
        Search for high-paying companies in the preferred locations using LLM analysis.
        
        Args:
            company_agent_state: State containing search parameters including:
                - locations: List of preferred locations
                - keywords: List of skill keywords
                - candidate: Candidate profile
                - include_remote: Whether to include remote companies
                - max_results: Maximum number of companies to return
                
        Returns:
            CompanySearchResponse with list of companies to search for jobs
        """
        locations = company_agent_state.get("locations", [])
        keywords = company_agent_state.get("keywords", [])
        candidate = company_agent_state.get("candidate")
        include_remote = company_agent_state.get("include_remote", True)
        max_results = company_agent_state.get("max_results", 20)
        
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
        Based on the following candidate profile and search criteria, identify the best companies to search for job opportunities:

        Candidate Profile:
        - Name: {context['candidate_name']}
        - Skills: {', '.join(context['candidate_skills'])}
        - Years of Experience: {context['candidate_experience']}
        - Preferred Locations: {', '.join(context['preferred_locations'])}
        - Salary Expectation: {f"${context['salary_expectation']:,}" if context['salary_expectation'] else "Not specified"}
        - Remote Preference: {', '.join(context['remote_preference'])}
        - Include Remote Companies: {context['include_remote']}

        Please identify up to {context['max_companies']} companies that:
        1. Are located in or near the preferred locations
        2. Pay competitive salaries for the candidate's skill set
        3. Are actively hiring for relevant positions
        4. Match the candidate's work arrangement preferences
        5. Have a good reputation and growth potential

        For each company, provide:
        - Company name
        - Location
        - Industry
        - Company size (startup, mid-size, enterprise)
        - Estimated average salary for the role
        - Current hiring status
        - Remote work support
        - Reasoning for selection

        Focus on companies that would be most attractive to this candidate based on their specific profile and preferences.
        """
        
        # Call LLM to get company recommendations
        try:
            breakpoint()
            response: CompanySearchResponse = await self.run(
                prompt
            )
            
            # Ensure we don't exceed max_results
            if len(response.companies) > max_results:
                response.companies = response.companies[:max_results]
                response.total_companies_found = len(response.companies)
            
            return response
            
        except Exception as e:
            logger.error(f"Error searching for companies: {e}")
            # Return fallback companies if LLM call fails
            fallback_companies = [
                CompanySearchResult(
                    company_name="Tech Company A",
                    location=locations[0] if locations else "San Francisco, CA",
                    industry="Technology",
                    company_size="mid-size",
                    average_salary=120000,
                    hiring_status="active",
                    remote_friendly=True,
                    reasoning="Fallback company due to LLM error"
                )
            ]
            
            return CompanySearchResponse(
                companies=fallback_companies,
                search_criteria=context,
                total_companies_found=len(fallback_companies)
            )


class JobFinderAgent(Agent):
    """Agent responsible for finding jobs."""
    
    model_config = ConfigDict(extra="forbid")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.output_type = JobSearchResponse
        self.system_prompt = """You are an expert recruiter specializing in finding active job postings from company websites and job boards. Your goal is to identify and extract detailed information about job opportunities that match the candidate's profile.

When searching for jobs, you should:

1. **Search Company Career Pages**: Look for active job postings on the company's official career website
2. **Check Job Boards**: Search major job boards like LinkedIn, Indeed, Glassdoor, and company-specific job sites
3. **Verify Job Status**: Ensure jobs are currently active and accepting applications
4. **Extract Complete Information**: Gather all relevant details including:
   - Job title and description
   - Salary information (if available)
   - Required skills and experience levels
   - Benefits and perks
   - Application deadlines
   - Work arrangement (remote/hybrid/on-site)

5. **Match Candidate Profile**: Prioritize jobs that align with:
   - Candidate's skills and experience level
   - Preferred locations and work arrangements
   - Salary expectations
   - Career goals and preferences

6. **Provide Direct Links**: Always include direct links to the actual job postings for easy application

7. **Validate Information**: Ensure all extracted information is accurate and up-to-date

Focus on finding high-quality, relevant job opportunities that would be attractive to the candidate based on their specific profile and preferences."""

    async def get_active_jobs(self, company_agent_state: Dict[str, Any]) -> List[JobPosting]:
        """
        Get active jobs from the high paying companies using LLM-powered search.
        
        Args:
            company_agent_state: State containing company information and search parameters
            
        Returns:
            List of JobPosting objects with direct links to company job postings
        """
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
                "company_size": company_detail.company_size if company_detail else "mid-size",
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
            - Size: {search_context['company_size']}

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

            For each job found, provide:
            - Job title
            - Company name
            - Job location
            - Salary range (if available)
            - Job description
            - Required skills and experience levels
            - Benefits offered
            - Direct link to the job posting
            - Posted date (if available)
            - Source of the job posting

            Focus on jobs that:
            - Are currently active and accepting applications
            - Match the candidate's skills and experience
            - Are in preferred locations or offer desired work arrangements
            - Have competitive salaries
            - Have direct application links

            Return up to 5 most relevant job postings for this company, along with the search sources used.
            """
            
            try:
                # Call LLM to search for jobs at this company
                response: JobSearchResponse = await self.run(
                    search_prompt,
                )
                # Add jobs from this company to the total list
                all_jobs.extend(response.jobs)
                
            except Exception as e:
                logger.error(f"Error searching for jobs at {company_name}: {e}")
                # Create fallback job posting if LLM call fails
                fallback_job = JobPosting(
                    title=f"Software Engineer - {search_context['candidate_skills'][0] if search_context['candidate_skills'] else 'General'}",
                    company=company_name,
                    location=search_context['company_location'],
                    salary_range=f"${80000}-${120000}",
                    salary_min=80000,
                    salary_max=120000,
                    description=f"Software engineering position at {company_name} requiring {', '.join(search_context['candidate_skills'])} skills.",
                    requirements=[
                        JobRequirement(skill=skill, level="mid", is_mandatory=True)
                        for skill in search_context['candidate_skills'][:3]
                    ],
                    benefits=["Health insurance", "401k", "Remote work options"],
                    job_url=f"https://{company_name.lower().replace(' ', '').replace('.', '')}.com/careers",
                    posted_date=datetime.now(),
                    match_score=75.0,
                    source=f"{company_name} (fallback)"
                )
                all_jobs.append(fallback_job)
        
        # Limit total results and sort by match score
        all_jobs.sort(key=lambda x: x.match_score or 0, reverse=True)
        return all_jobs[:max_results]

    async def filter_jobs(self, company_agent_state: Dict[str, Any]) -> List[JobPosting]:
        """
        Filter jobs based on candidate skills, salary expectations, and preferences.
        """
        active_jobs = company_agent_state.get("active_jobs", [])
        candidate = company_agent_state.get("candidate")
        salary_threshold = company_agent_state.get("salary_threshold")
        
        if not candidate:
            return active_jobs
        
        filtered_jobs = []
        
        for job in active_jobs:
            # Filter by salary threshold
            if salary_threshold and job.salary_min and job.salary_min < salary_threshold:
                continue
                
            # Filter by candidate salary expectation
            if candidate.salary_expectation and job.salary_max and job.salary_max < candidate.salary_expectation * 0.8:
                continue
            
            # Filter by location preferences
            location_match = False
            for pref_location in candidate.preferred_locations:
                if (pref_location.city.lower() in job.location.lower() or
                    (pref_location.state and pref_location.state.lower() in job.location.lower()) or
                    (pref_location.remote_preference == "remote" and "remote" in job.location.lower())):
                    location_match = True
                    break
            
            if not location_match:
                continue
            
            filtered_jobs.append(job)
        
        # Sort by match score (highest first)
        filtered_jobs.sort(key=lambda x: x.match_score or 0, reverse=True)
        
        return filtered_jobs


# =============================================================================
# Main Orchestrator Agent
# =============================================================================

class JobFinderOrchestratorAgent(Agent):
    """
    Main orchestrator agent that coordinates all specialized agents to find
    the best job opportunities for candidates.
    """
    
    model_config = ConfigDict(extra="forbid")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        model = kwargs.get("model", config.DEFAULT_MODEL)
        self.model = model
        self.company_finder: CompanyFinderAgent = CompanyFinderAgent(model=model)
        self.job_finder: JobFinderAgent = JobFinderAgent(model=model)

    async def find_jobs(self, request: JobSearchRequest) -> JobSearchResult:
        """
        Main method to find jobs for a candidate.
        
        Args:
            request: Job search request with candidate profile
            
        Returns:
            Job search results with ranked job postings
        """
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
        
        avg_salary = sum(job.salary_min or 0 for job in jobs if job.salary_min) / len([j for j in jobs if j.salary_min])
        avg_match_score = sum(job.match_score or 0 for job in jobs) / len(jobs)
        
        top_jobs = jobs[:3]
        top_companies = [job.company for job in top_jobs]
        
        summary = f"""
        Found {len(jobs)} suitable jobs for {candidate.name} in {duration:.2f} seconds.
        
        Top opportunities:
        - Average salary: ${avg_salary:,.0f}
        - Average match score: {avg_match_score:.1f}%
        - Top companies: {', '.join(top_companies)}
        
        Best matches:
        """
        
        for i, job in enumerate(top_jobs, 1):
            summary += f"{i}. {job.title} at {job.company} ({job.match_score}% match)\n"
        
        return summary.strip()


# =============================================================================
# Factory Functions
# =============================================================================

def create_job_finder_agent(openai_api_key: str) -> JobFinderOrchestratorAgent:
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
    
    return JobFinderOrchestratorAgent(
        model="gpt-4",
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
        max_results=20,
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
