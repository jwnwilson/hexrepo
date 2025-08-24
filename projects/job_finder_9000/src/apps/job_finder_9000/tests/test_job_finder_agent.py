"""
Tests for the JobFinderAgent
"""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from apps.job_finder_9000.domain.job_finder_agent import (
    JobFinderAgent,
    JobSearchResponse,
    JobPosting,
    JobRequirement,
    CandidateProfile,
    Skill,
    Location,
    CompanySearchResult
)


class TestJobFinderAgent:
    """Test cases for JobFinderAgent"""
    
    @pytest.fixture
    def agent(self):
        """Create a JobFinderAgent instance for testing"""
        return JobFinderAgent()
    
    @pytest.fixture
    def sample_candidate(self):
        """Create a sample candidate profile for testing"""
        return CandidateProfile(
            name="John Doe",
            email="john.doe@example.com",
            skills=[
                Skill(name="Python", proficiency="expert", years_experience=5),
                Skill(name="JavaScript", proficiency="intermediate", years_experience=3),
            ],
            experience_years=5,
            preferred_locations=[
                Location(city="San Francisco", state="CA", country="USA", remote_preference="hybrid"),
                Location(city="New York", state="NY", country="USA", remote_preference="hybrid"),
            ],
            salary_expectation=120000,
            job_preferences={"industry": "tech", "company_size": "startup"}
        )
    
    @pytest.fixture
    def sample_company_details(self):
        """Create sample company details for testing"""
        return [
            CompanySearchResult(
                company_name="Google",
                location="Mountain View, CA",
                industry="Technology",
                company_size="enterprise",
                average_salary=150000,
                hiring_status="active",
                remote_friendly=True,
                reasoning="High-paying tech company"
            ),
            CompanySearchResult(
                company_name="Meta",
                location="Menlo Park, CA",
                industry="Technology",
                company_size="enterprise",
                average_salary=140000,
                hiring_status="active",
                remote_friendly=True,
                reasoning="Leading social media company"
            )
        ]
    
    def test_agent_initialization(self, agent):
        """Test that the agent initializes with the correct system prompt"""
        assert agent.system_prompt is not None
        assert "recruiter" in agent.system_prompt.lower()
        assert "active job postings" in agent.system_prompt.lower()
        assert "company websites" in agent.system_prompt.lower()
    
    @pytest.mark.asyncio
    async def test_get_active_jobs_success(self, agent, sample_candidate, sample_company_details):
        """Test successful job search with LLM response"""
        # Mock LLM response for Google
        google_jobs = JobSearchResponse(
            jobs=[
                JobPosting(
                    title="Senior Software Engineer - Python",
                    company="Google",
                    location="Mountain View, CA",
                    salary_range="$150,000-$200,000",
                    salary_min=150000,
                    salary_max=200000,
                    description="Join Google's engineering team...",
                    requirements=[
                        JobRequirement(skill="Python", level="senior", is_mandatory=True),
                        JobRequirement(skill="JavaScript", level="mid", is_mandatory=False)
                    ],
                    benefits=["Health insurance", "401k", "Free meals"],
                    job_url="https://careers.google.com/jobs/123",
                    posted_date=datetime.now(),
                    match_score=90.0,
                    source="Google Careers"
                )
            ],
            company_name="Google",
            total_jobs_found=1,
            search_sources=["Google Careers", "LinkedIn"]
        )
        
        # Mock LLM response for Meta
        meta_jobs = JobSearchResponse(
            jobs=[
                JobPosting(
                    title="Full Stack Engineer",
                    company="Meta",
                    location="Menlo Park, CA",
                    salary_range="$140,000-$180,000",
                    salary_min=140000,
                    salary_max=180000,
                    description="Build the next generation of social media...",
                    requirements=[
                        JobRequirement(skill="JavaScript", level="senior", is_mandatory=True),
                        JobRequirement(skill="React", level="mid", is_mandatory=True)
                    ],
                    benefits=["Health insurance", "401k", "Remote work"],
                    job_url="https://careers.meta.com/jobs/456",
                    posted_date=datetime.now(),
                    match_score=85.0,
                    source="Meta Careers"
                )
            ],
            company_name="Meta",
            total_jobs_found=1,
            search_sources=["Meta Careers", "Indeed"]
        )
        
        company_agent_state = {
            "companies": ["Google", "Meta"],
            "company_details": sample_company_details,
            "candidate": sample_candidate,
            "keywords": ["Python", "JavaScript"],
            "max_results": 10
        }
        
        with patch.object(agent, 'ainvoke', new_callable=AsyncMock) as mock_ainvoke:
            # Mock different responses for different companies
            mock_ainvoke.side_effect = [google_jobs, meta_jobs]
            
            result = await agent.get_active_jobs(company_agent_state)
            
            # Verify the result
            assert len(result) == 2
            assert result[0].company == "Google"
            assert result[0].title == "Senior Software Engineer - Python"
            assert result[1].company == "Meta"
            assert result[1].title == "Full Stack Engineer"
            
            # Verify LLM was called for each company
            assert mock_ainvoke.call_count == 2
            
            # Verify the calls were made with correct parameters
            calls = mock_ainvoke.call_args_list
            assert "Google" in calls[0][0][0]  # First call should mention Google
            assert "Meta" in calls[1][0][0]    # Second call should mention Meta
            assert calls[0][1]['response_model'] == JobSearchResponse
            assert calls[0][1]['system_prompt'] == agent.system_prompt
    
    @pytest.mark.asyncio
    async def test_get_active_jobs_fallback_on_error(self, agent, sample_candidate, sample_company_details):
        """Test fallback behavior when LLM call fails"""
        company_agent_state = {
            "companies": ["Google"],
            "company_details": sample_company_details,
            "candidate": sample_candidate,
            "keywords": ["Python"],
            "max_results": 5
        }
        
        with patch.object(agent, 'ainvoke', new_callable=AsyncMock) as mock_ainvoke:
            mock_ainvoke.side_effect = Exception("LLM API error")
            
            result = await agent.get_active_jobs(company_agent_state)
            
            # Verify fallback response
            assert len(result) == 1
            assert result[0].company == "Google"
            assert "Software Engineer" in result[0].title
            assert result[0].source == "Google (fallback)"
            assert result[0].match_score == 75.0
    
    @pytest.mark.asyncio
    async def test_get_active_jobs_respects_max_results(self, agent, sample_candidate, sample_company_details):
        """Test that the agent respects the max_results parameter"""
        # Create mock response with many jobs
        many_jobs = [
            JobPosting(
                title=f"Software Engineer {i}",
                company="Google",
                location="Mountain View, CA",
                salary_range="$120,000-$160,000",
                salary_min=120000,
                salary_max=160000,
                description=f"Job description {i}",
                requirements=[],
                benefits=[],
                job_url=f"https://google.com/jobs/{i}",
                posted_date=datetime.now(),
                match_score=90.0 - i,
                source="Google Careers"
            )
            for i in range(10)  # More than max_results=5
        ]
        
        mock_response = JobSearchResponse(
            jobs=many_jobs,
            company_name="Google",
            total_jobs_found=10,
            search_sources=["Google Careers"]
        )
        
        company_agent_state = {
            "companies": ["Google"],
            "company_details": sample_company_details,
            "candidate": sample_candidate,
            "keywords": ["Python"],
            "max_results": 5
        }
        
        with patch.object(agent, 'ainvoke', new_callable=AsyncMock) as mock_ainvoke:
            mock_ainvoke.return_value = mock_response
            
            result = await agent.get_active_jobs(company_agent_state)
            
            # Verify that only max_results jobs are returned
            assert len(result) == 5
            assert result[0].title == "Software Engineer 0"  # Highest match score
            assert result[4].title == "Software Engineer 4"  # Lower match score
    
    @pytest.mark.asyncio
    async def test_get_active_jobs_empty_companies(self, agent, sample_candidate):
        """Test behavior when no companies are provided"""
        company_agent_state = {
            "companies": [],
            "company_details": [],
            "candidate": sample_candidate,
            "keywords": ["Python"],
            "max_results": 10
        }
        
        result = await agent.get_active_jobs(company_agent_state)
        
        # Should return empty list when no companies
        assert result == []
    
    def test_system_prompt_content(self, agent):
        """Test that the system prompt contains expected content"""
        prompt = agent.system_prompt.lower()
        
        # Check for key concepts
        assert "recruiter" in prompt
        assert "active job postings" in prompt
        assert "company websites" in prompt
        assert "job boards" in prompt
        assert "linkedin" in prompt
        assert "indeed" in prompt
        assert "glassdoor" in prompt
        assert "direct links" in prompt
        assert "candidate profile" in prompt 