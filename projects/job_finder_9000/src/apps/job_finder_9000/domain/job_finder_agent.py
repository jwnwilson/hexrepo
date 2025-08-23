"""
Job Finder Agent System

This module implements a comprehensive job finding system using Pydantic AI agents.
The system orchestrates multiple specialized agents to find the highest paid and
most suitable jobs for candidates based on their skills and location preferences.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

from pydantic import BaseModel, Field, ConfigDict
from pydantic_ai import Agent, AgentConfig
from pydantic_ai.tools import tool
import aiohttp
import requests
from bs4 import BeautifulSoup

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

class SkillMatcherAgent(Agent):
    """Agent responsible for matching candidate skills to job requirements."""
    
    model_config = ConfigDict(extra="forbid")
    
    @tool
    def calculate_skill_match_score(self, candidate_skills: List[Skill], job_requirements: List[JobRequirement]) -> float:
        """
        Calculate a match score between candidate skills and job requirements.
        
        Args:
            candidate_skills: List of candidate skills
            job_requirements: List of job requirements
            
        Returns:
            Match score from 0 to 100
        """
        if not candidate_skills or not job_requirements:
            return 0.0
        
        # Create skill mapping
        candidate_skill_map = {
            skill.name.lower(): skill for skill in candidate_skills
        }
        
        total_score = 0
        mandatory_matches = 0
        total_mandatory = sum(1 for req in job_requirements if req.is_mandatory)
        
        for requirement in job_requirements:
            skill_name = requirement.skill.lower()
            
            if skill_name in candidate_skill_map:
                candidate_skill = candidate_skill_map[skill_name]
                
                # Calculate proficiency match
                proficiency_score = self._calculate_proficiency_match(
                    candidate_skill.proficiency, requirement.level
                )
                
                # Weight mandatory requirements more heavily
                weight = 2.0 if requirement.is_mandatory else 1.0
                total_score += proficiency_score * weight
                
                if requirement.is_mandatory:
                    mandatory_matches += 1
        
        # Penalize if mandatory requirements are not met
        if total_mandatory > 0:
            mandatory_ratio = mandatory_matches / total_mandatory
            if mandatory_ratio < 0.8:  # Require at least 80% of mandatory skills
                return 0.0
        
        # Normalize score to 0-100
        max_possible_score = len(job_requirements) * 2.0  # Assuming all requirements are mandatory
        final_score = min(100.0, (total_score / max_possible_score) * 100)
        
        return round(final_score, 2)
    
    def _calculate_proficiency_match(self, candidate_level: str, required_level: str) -> float:
        """Calculate proficiency match between candidate and requirement levels."""
        level_mapping = {
            "beginner": 1,
            "entry": 1,
            "intermediate": 2,
            "mid": 2,
            "expert": 3,
            "senior": 3,
            "lead": 4
        }
        
        candidate_score = level_mapping.get(candidate_level.lower(), 1)
        required_score = level_mapping.get(required_level.lower(), 1)
        
        if candidate_score >= required_score:
            return 1.0
        elif candidate_score >= required_score - 1:
            return 0.7
        else:
            return 0.3


class JobScraperAgent(Agent):
    """Agent responsible for scraping job postings from various sources."""
    
    model_config = ConfigDict(extra="forbid")
    
    @tool
    async def scrape_linkedin_jobs(self, keywords: List[str], location: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Scrape job postings from LinkedIn (simulated).
        
        Args:
            keywords: List of job keywords
            location: Job location
            max_results: Maximum number of results
            
        Returns:
            List of job postings
        """
        # This is a simulated implementation
        # In a real implementation, you would use LinkedIn's API or web scraping
        jobs = []
        
        for i in range(min(max_results, 10)):
            jobs.append({
                "title": f"Software Engineer - {keywords[0] if keywords else 'General'}",
                "company": f"Tech Company {i+1}",
                "location": location,
                "salary_range": f"${80000 + i*10000}-${120000 + i*10000}",
                "salary_min": 80000 + i*10000,
                "salary_max": 120000 + i*10000,
                "description": f"Looking for a {keywords[0] if keywords else 'software'} engineer...",
                "requirements": [
                    {"skill": "Python", "level": "mid", "is_mandatory": True},
                    {"skill": "JavaScript", "level": "entry", "is_mandatory": False}
                ],
                "benefits": ["Health insurance", "401k", "Remote work"],
                "job_url": f"https://linkedin.com/jobs/{i}",
                "posted_date": datetime.now().isoformat(),
                "source": "LinkedIn"
            })
        
        return jobs
    
    @tool
    async def scrape_indeed_jobs(self, keywords: List[str], location: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Scrape job postings from Indeed (simulated).
        
        Args:
            keywords: List of job keywords
            location: Job location
            max_results: Maximum number of results
            
        Returns:
            List of job postings
        """
        # This is a simulated implementation
        jobs = []
        
        for i in range(min(max_results, 10)):
            jobs.append({
                "title": f"Senior {keywords[0] if keywords else 'Developer'}",
                "company": f"Startup {i+1}",
                "location": location,
                "salary_range": f"${90000 + i*15000}-${140000 + i*15000}",
                "salary_min": 90000 + i*15000,
                "salary_max": 140000 + i*15000,
                "description": f"Join our team as a senior {keywords[0] if keywords else 'developer'}...",
                "requirements": [
                    {"skill": "Python", "level": "senior", "is_mandatory": True},
                    {"skill": "AWS", "level": "mid", "is_mandatory": True}
                ],
                "benefits": ["Equity", "Flexible hours", "Learning budget"],
                "job_url": f"https://indeed.com/jobs/{i}",
                "posted_date": datetime.now().isoformat(),
                "source": "Indeed"
            })
        
        return jobs
    
    @tool
    async def scrape_glassdoor_jobs(self, keywords: List[str], location: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Scrape job postings from Glassdoor (simulated).
        
        Args:
            keywords: List of job keywords
            location: Job location
            max_results: Maximum number of results
            
        Returns:
            List of job postings
        """
        # This is a simulated implementation
        jobs = []
        
        for i in range(min(max_results, 10)):
            jobs.append({
                "title": f"{keywords[0] if keywords else 'Full Stack'} Developer",
                "company": f"Enterprise Corp {i+1}",
                "location": location,
                "salary_range": f"${85000 + i*12000}-${130000 + i*12000}",
                "salary_min": 85000 + i*12000,
                "salary_max": 130000 + i*12000,
                "description": f"Enterprise {keywords[0] if keywords else 'full stack'} developer position...",
                "requirements": [
                    {"skill": "Java", "level": "mid", "is_mandatory": True},
                    {"skill": "Spring", "level": "entry", "is_mandatory": False}
                ],
                "benefits": ["Pension", "Health insurance", "Paid time off"],
                "job_url": f"https://glassdoor.com/jobs/{i}",
                "posted_date": datetime.now().isoformat(),
                "source": "Glassdoor"
            })
        
        return jobs


class SalaryAnalyzerAgent(Agent):
    """Agent responsible for analyzing and comparing salaries."""
    
    model_config = ConfigDict(extra="forbid")
    
    @tool
    def analyze_salary_market_rate(self, job_title: str, location: str, experience_years: int) -> Dict[str, Any]:
        """
        Analyze market salary rates for a given job title and location.
        
        Args:
            job_title: The job title to analyze
            location: The location for salary analysis
            experience_years: Years of experience
            
        Returns:
            Salary analysis data
        """
        # This is a simulated implementation
        # In a real implementation, you would query salary databases or APIs
        
        base_salary = 70000
        location_multiplier = 1.2 if "San Francisco" in location or "New York" in location else 1.0
        experience_multiplier = 1.0 + (experience_years * 0.1)
        
        market_rate = int(base_salary * location_multiplier * experience_multiplier)
        
        return {
            "market_rate": market_rate,
            "percentile_25": int(market_rate * 0.8),
            "percentile_50": market_rate,
            "percentile_75": int(market_rate * 1.2),
            "percentile_90": int(market_rate * 1.4),
            "location_multiplier": location_multiplier,
            "experience_multiplier": experience_multiplier
        }
    
    @tool
    def calculate_salary_score(self, job_salary: int, market_rate: int, candidate_expectation: Optional[int] = None) -> float:
        """
        Calculate a salary score for a job posting.
        
        Args:
            job_salary: The job salary
            market_rate: The market rate for the position
            candidate_expectation: Candidate's salary expectation
            
        Returns:
            Salary score from 0 to 100
        """
        if job_salary <= 0:
            return 0.0
        
        # Base score based on market rate comparison
        if job_salary >= market_rate * 1.2:
            base_score = 100.0
        elif job_salary >= market_rate:
            base_score = 80.0
        elif job_salary >= market_rate * 0.8:
            base_score = 60.0
        else:
            base_score = 30.0
        
        # Adjust for candidate expectation if provided
        if candidate_expectation:
            if job_salary >= candidate_expectation:
                expectation_bonus = 20.0
            elif job_salary >= candidate_expectation * 0.9:
                expectation_bonus = 10.0
            else:
                expectation_bonus = -20.0
            
            final_score = min(100.0, max(0.0, base_score + expectation_bonus))
        else:
            final_score = base_score
        
        return round(final_score, 2)


class LocationAnalyzerAgent(Agent):
    """Agent responsible for analyzing location preferences and job availability."""
    
    model_config = ConfigDict(extra="forbid")
    
    @tool
    def analyze_location_preferences(self, candidate_locations: List[Location], job_location: str) -> float:
        """
        Analyze how well a job location matches candidate preferences.
        
        Args:
            candidate_locations: Candidate's preferred locations
            job_location: Job location string
            
        Returns:
            Location match score from 0 to 100
        """
        if not candidate_locations:
            return 50.0  # Neutral score if no preferences
        
        best_match = 0.0
        
        for pref_location in candidate_locations:
            # Exact city match
            if pref_location.city.lower() in job_location.lower():
                match_score = 100.0
            # State match
            elif pref_location.state and pref_location.state.lower() in job_location.lower():
                match_score = 80.0
            # Country match
            elif pref_location.country.lower() in job_location.lower():
                match_score = 60.0
            # Remote preference
            elif pref_location.remote_preference == "remote" and "remote" in job_location.lower():
                match_score = 90.0
            else:
                match_score = 20.0
            
            best_match = max(best_match, match_score)
        
        return best_match


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
        self.skill_matcher = SkillMatcherAgent()
        self.job_scraper = JobScraperAgent()
        self.salary_analyzer = SalaryAnalyzerAgent()
        self.location_analyzer = LocationAnalyzerAgent()
    
    @tool
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
            locations = ["Remote"] if include_remote else ["Any"]
        
        # Scrape jobs from multiple sources
        all_jobs = []
        sources_searched = []
        
        for location in locations:
            # Scrape from LinkedIn
            try:
                linkedin_jobs = await self.job_scraper.scrape_linkedin_jobs(
                    keywords, location, max_results // len(locations)
                )
                all_jobs.extend(linkedin_jobs)
                sources_searched.append("LinkedIn")
            except Exception as e:
                logger.error(f"Error scraping LinkedIn jobs: {e}")
            
            # Scrape from Indeed
            try:
                indeed_jobs = await self.job_scraper.scrape_indeed_jobs(
                    keywords, location, max_results // len(locations)
                )
                all_jobs.extend(indeed_jobs)
                sources_searched.append("Indeed")
            except Exception as e:
                logger.error(f"Error scraping Indeed jobs: {e}")
            
            # Scrape from Glassdoor
            try:
                glassdoor_jobs = await self.job_scraper.scrape_glassdoor_jobs(
                    keywords, location, max_results // len(locations)
                )
                all_jobs.extend(glassdoor_jobs)
                sources_searched.append("Glassdoor")
            except Exception as e:
                logger.error(f"Error scraping Glassdoor jobs: {e}")
        
        # Convert to JobPosting objects and calculate scores
        job_postings = []
        for job_data in all_jobs:
            try:
                job_posting = JobPosting(**job_data)
                
                # Calculate skill match score
                skill_score = self.skill_matcher.calculate_skill_match_score(
                    candidate.skills, job_posting.requirements
                )
                
                # Calculate salary score
                if job_posting.salary_min:
                    market_rate = self.salary_analyzer.analyze_salary_market_rate(
                        job_posting.title, job_posting.location, candidate.experience_years
                    )["market_rate"]
                    
                    salary_score = self.salary_analyzer.calculate_salary_score(
                        job_posting.salary_min, market_rate, candidate.salary_expectation
                    )
                else:
                    salary_score = 50.0  # Neutral score if no salary info
                
                # Calculate location score
                location_score = self.location_analyzer.analyze_location_preferences(
                    candidate.preferred_locations, job_posting.location
                )
                
                # Calculate overall match score (weighted average)
                overall_score = (skill_score * 0.5 + salary_score * 0.3 + location_score * 0.2)
                job_posting.match_score = round(overall_score, 2)
                
                job_postings.append(job_posting)
                
            except Exception as e:
                logger.error(f"Error processing job posting: {e}")
                continue
        
        # Sort by match score (highest first) and limit results
        job_postings.sort(key=lambda x: x.match_score or 0, reverse=True)
        job_postings = job_postings[:max_results]
        
        # Calculate search duration
        end_time = datetime.now()
        search_duration = (end_time - start_time).total_seconds()
        
        # Generate summary
        summary = self._generate_search_summary(job_postings, candidate, search_duration)
        
        return JobSearchResult(
            jobs=job_postings,
            total_found=len(job_postings),
            search_duration=search_duration,
            sources_searched=list(set(sources_searched)),
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
    config = AgentConfig(
        model="gpt-4",
        api_key=openai_api_key,
        temperature=0.1,
        max_tokens=4000
    )
    
    return JobFinderOrchestratorAgent(config=config)


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
