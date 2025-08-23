"""
Tests for Job Finder Agent

This module contains tests for the job finder agent system.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime

from ..domain.job_finder_agent import (
    SkillMatcherAgent,
    JobScraperAgent,
    SalaryAnalyzerAgent,
    LocationAnalyzerAgent,
    JobFinderOrchestratorAgent,
    create_job_finder_agent,
    CandidateProfile,
    Skill,
    Location,
    JobRequirement,
    JobPosting,
    JobSearchRequest,
    JobSearchResult
)
from ..services.job_finder_service import JobFinderService


class TestSkillMatcherAgent:
    """Test cases for SkillMatcherAgent."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = SkillMatcherAgent()
        
        self.candidate_skills = [
            Skill(name="Python", proficiency="expert", years_experience=5),
            Skill(name="JavaScript", proficiency="intermediate", years_experience=3),
            Skill(name="AWS", proficiency="beginner", years_experience=1),
        ]
        
        self.job_requirements = [
            JobRequirement(skill="Python", level="senior", is_mandatory=True),
            JobRequirement(skill="JavaScript", level="mid", is_mandatory=False),
            JobRequirement(skill="Docker", level="entry", is_mandatory=False),
        ]
    
    def test_calculate_skill_match_score_perfect_match(self):
        """Test skill matching with perfect candidate-job alignment."""
        score = self.agent.calculate_skill_match_score(
            self.candidate_skills, self.job_requirements
        )
        
        # Should have a high score due to Python expert matching senior requirement
        assert score > 70
        assert score <= 100
    
    def test_calculate_skill_match_score_no_match(self):
        """Test skill matching with no relevant skills."""
        candidate_skills = [
            Skill(name="Java", proficiency="expert", years_experience=5),
        ]
        
        score = self.agent.calculate_skill_match_score(
            candidate_skills, self.job_requirements
        )
        
        # Should have a low score due to no matching skills
        assert score < 30
    
    def test_calculate_skill_match_score_missing_mandatory(self):
        """Test skill matching when mandatory requirements are not met."""
        job_requirements = [
            JobRequirement(skill="Python", level="senior", is_mandatory=True),
            JobRequirement(skill="Java", level="mid", is_mandatory=True),
        ]
        
        score = self.agent.calculate_skill_match_score(
            self.candidate_skills, job_requirements
        )
        
        # Should have a very low score due to missing mandatory Java skill
        assert score < 50
    
    def test_calculate_proficiency_match(self):
        """Test proficiency level matching."""
        # Expert should match senior requirement
        assert self.agent._calculate_proficiency_match("expert", "senior") == 1.0
        
        # Intermediate should partially match senior requirement
        assert self.agent._calculate_proficiency_match("intermediate", "senior") == 0.7
        
        # Beginner should have low match for senior requirement
        assert self.agent._calculate_proficiency_match("beginner", "senior") == 0.3


class TestJobScraperAgent:
    """Test cases for JobScraperAgent."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = JobScraperAgent()
    
    @pytest.mark.asyncio
    async def test_scrape_linkedin_jobs(self):
        """Test LinkedIn job scraping."""
        keywords = ["Python", "Django"]
        location = "San Francisco"
        
        jobs = await self.agent.scrape_linkedin_jobs(keywords, location, max_results=5)
        
        assert len(jobs) <= 5
        assert all(isinstance(job, dict) for job in jobs)
        assert all("title" in job for job in jobs)
        assert all("company" in job for job in jobs)
        assert all("location" in job for job in jobs)
    
    @pytest.mark.asyncio
    async def test_scrape_indeed_jobs(self):
        """Test Indeed job scraping."""
        keywords = ["JavaScript", "React"]
        location = "New York"
        
        jobs = await self.agent.scrape_indeed_jobs(keywords, location, max_results=3)
        
        assert len(jobs) <= 3
        assert all(isinstance(job, dict) for job in jobs)
        assert all("title" in job for job in jobs)
    
    @pytest.mark.asyncio
    async def test_scrape_glassdoor_jobs(self):
        """Test Glassdoor job scraping."""
        keywords = ["Java", "Spring"]
        location = "Austin"
        
        jobs = await self.agent.scrape_glassdoor_jobs(keywords, location, max_results=4)
        
        assert len(jobs) <= 4
        assert all(isinstance(job, dict) for job in jobs)
        assert all("title" in job for job in jobs)


class TestSalaryAnalyzerAgent:
    """Test cases for SalaryAnalyzerAgent."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = SalaryAnalyzerAgent()
    
    def test_analyze_salary_market_rate(self):
        """Test market rate analysis."""
        analysis = self.agent.analyze_salary_market_rate(
            "Software Engineer", "San Francisco", 5
        )
        
        assert "market_rate" in analysis
        assert "percentile_25" in analysis
        assert "percentile_50" in analysis
        assert "percentile_75" in analysis
        assert "percentile_90" in analysis
        assert analysis["market_rate"] > 0
    
    def test_analyze_salary_market_rate_high_cost_location(self):
        """Test market rate analysis for high-cost locations."""
        sf_analysis = self.agent.analyze_salary_market_rate(
            "Software Engineer", "San Francisco", 3
        )
        
        ny_analysis = self.agent.analyze_salary_market_rate(
            "Software Engineer", "New York", 3
        )
        
        # High-cost locations should have higher market rates
        assert sf_analysis["market_rate"] > 70000
        assert ny_analysis["market_rate"] > 70000
    
    def test_calculate_salary_score_above_market(self):
        """Test salary scoring for above-market salaries."""
        score = self.agent.calculate_salary_score(
            job_salary=120000,
            market_rate=100000,
            candidate_expectation=110000
        )
        
        # Should have a high score for above-market salary
        assert score > 80
    
    def test_calculate_salary_score_below_market(self):
        """Test salary scoring for below-market salaries."""
        score = self.agent.calculate_salary_score(
            job_salary=70000,
            market_rate=100000,
            candidate_expectation=90000
        )
        
        # Should have a lower score for below-market salary
        assert score < 70


class TestLocationAnalyzerAgent:
    """Test cases for LocationAnalyzerAgent."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = LocationAnalyzerAgent()
        
        self.candidate_locations = [
            Location(city="San Francisco", state="CA", country="USA", remote_preference="hybrid"),
            Location(city="New York", state="NY", country="USA", remote_preference="on-site"),
        ]
    
    def test_analyze_location_preferences_exact_match(self):
        """Test location matching with exact city match."""
        score = self.agent.analyze_location_preferences(
            self.candidate_locations, "San Francisco, CA"
        )
        
        # Should have perfect score for exact match
        assert score == 100.0
    
    def test_analyze_location_preferences_state_match(self):
        """Test location matching with state match."""
        score = self.agent.analyze_location_preferences(
            self.candidate_locations, "Los Angeles, CA"
        )
        
        # Should have high score for state match
        assert score == 80.0
    
    def test_analyze_location_preferences_remote_match(self):
        """Test location matching with remote preference."""
        remote_locations = [
            Location(city="Any", state=None, country="Any", remote_preference="remote")
        ]
        
        score = self.agent.analyze_location_preferences(
            remote_locations, "Remote"
        )
        
        # Should have high score for remote match
        assert score == 90.0
    
    def test_analyze_location_preferences_no_match(self):
        """Test location matching with no relevant match."""
        score = self.agent.analyze_location_preferences(
            self.candidate_locations, "London, UK"
        )
        
        # Should have low score for no match
        assert score == 20.0


class TestJobFinderOrchestratorAgent:
    """Test cases for JobFinderOrchestratorAgent."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = JobFinderOrchestratorAgent()
        
        self.candidate = CandidateProfile(
            name="Test User",
            email="test@example.com",
            skills=[
                Skill(name="Python", proficiency="expert", years_experience=5),
                Skill(name="JavaScript", proficiency="intermediate", years_experience=3),
            ],
            experience_years=5,
            preferred_locations=[
                Location(city="San Francisco", state="CA", country="USA", remote_preference="hybrid"),
            ],
            salary_expectation=120000
        )
        
        self.search_request = JobSearchRequest(
            candidate=self.candidate,
            max_results=10,
            include_remote=True,
            salary_threshold=80000
        )
    
    @pytest.mark.asyncio
    async def test_find_jobs(self):
        """Test the main job finding functionality."""
        result = await self.agent.find_jobs(self.search_request)
        
        assert isinstance(result, JobSearchResult)
        assert result.total_found >= 0
        assert result.search_duration >= 0
        assert len(result.sources_searched) > 0
        assert result.summary is not None
        
        # Check that jobs are sorted by match score (highest first)
        if len(result.jobs) > 1:
            scores = [job.match_score or 0 for job in result.jobs]
            assert scores == sorted(scores, reverse=True)
    
    def test_generate_search_summary(self):
        """Test search summary generation."""
        # Create mock job postings
        jobs = [
            JobPosting(
                title="Python Developer",
                company="Tech Corp",
                location="San Francisco, CA",
                salary_min=120000,
                salary_max=150000,
                description="Python developer role",
                job_url="https://example.com/job1",
                source="LinkedIn",
                match_score=85.0
            ),
            JobPosting(
                title="Software Engineer",
                company="Startup Inc",
                location="Remote",
                salary_min=100000,
                salary_max=130000,
                description="Software engineer role",
                job_url="https://example.com/job2",
                source="Indeed",
                match_score=75.0
            )
        ]
        
        summary = self.agent._generate_search_summary(jobs, self.candidate, 2.5)
        
        assert "Found 2 suitable jobs" in summary
        assert "Test User" in summary
        assert "2.50 seconds" in summary
        assert "Python Developer" in summary
        assert "Software Engineer" in summary


class TestJobFinderService:
    """Test cases for JobFinderService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = JobFinderService()
        
        self.candidate_data = {
            "name": "Test User",
            "email": "test@example.com",
            "skills": [
                {"name": "Python", "proficiency": "expert", "years_experience": 5},
                {"name": "JavaScript", "proficiency": "intermediate", "years_experience": 3},
            ],
            "experience_years": 5,
            "preferred_locations": [
                {"city": "San Francisco", "state": "CA", "country": "USA", "remote_preference": "hybrid"},
            ],
            "salary_expectation": 120000
        }
    
    def test_create_candidate_profile(self):
        """Test candidate profile creation from raw data."""
        profile = self.service.create_candidate_profile(
            name=self.candidate_data["name"],
            email=self.candidate_data["email"],
            skills=self.candidate_data["skills"],
            experience_years=self.candidate_data["experience_years"],
            preferred_locations=self.candidate_data["preferred_locations"],
            salary_expectation=self.candidate_data["salary_expectation"]
        )
        
        assert isinstance(profile, CandidateProfile)
        assert profile.name == "Test User"
        assert profile.email == "test@example.com"
        assert len(profile.skills) == 2
        assert len(profile.preferred_locations) == 1
        assert profile.salary_expectation == 120000
    
    @patch.object(JobFinderService, 'agent')
    def test_find_jobs_agent_not_initialized(self, mock_agent):
        """Test job search when agent is not initialized."""
        mock_agent.return_value = None
        
        profile = self.service.create_candidate_profile(
            name=self.candidate_data["name"],
            email=self.candidate_data["email"],
            skills=self.candidate_data["skills"],
            experience_years=self.candidate_data["experience_years"],
            preferred_locations=self.candidate_data["preferred_locations"],
            salary_expectation=self.candidate_data["salary_expectation"]
        )
        
        with pytest.raises(Exception, match="Job finder agent is not initialized"):
            self.service.find_jobs(profile)
    
    def test_analyze_candidate_market_position(self):
        """Test market position analysis."""
        profile = self.service.create_candidate_profile(
            name=self.candidate_data["name"],
            email=self.candidate_data["email"],
            skills=self.candidate_data["skills"],
            experience_years=self.candidate_data["experience_years"],
            preferred_locations=self.candidate_data["preferred_locations"],
            salary_expectation=self.candidate_data["salary_expectation"]
        )
        
        # Mock the agent to avoid actual API calls
        with patch.object(self.service, 'agent') as mock_agent:
            mock_agent.return_value = None
            
            analysis = self.service.analyze_candidate_market_position(profile)
            
            assert "market_demand" in analysis
            assert "average_salary" in analysis
            assert "salary_percentile" in analysis
            assert "skill_gaps" in analysis
            assert "recommendations" in analysis


class TestIntegration:
    """Integration tests for the complete job finder system."""
    
    def test_agent_creation(self):
        """Test agent creation with mock API key."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            agent = create_job_finder_agent("test-key")
            assert isinstance(agent, JobFinderOrchestratorAgent)
    
    def test_data_model_validation(self):
        """Test Pydantic model validation."""
        # Valid skill
        skill = Skill(name="Python", proficiency="expert", years_experience=5)
        assert skill.name == "Python"
        assert skill.proficiency == "expert"
        
        # Valid location
        location = Location(city="San Francisco", state="CA", country="USA")
        assert location.city == "San Francisco"
        assert location.remote_preference == "hybrid"  # default value
        
        # Valid job posting
        job = JobPosting(
            title="Python Developer",
            company="Tech Corp",
            location="San Francisco, CA",
            description="Python developer role",
            job_url="https://example.com/job",
            source="LinkedIn"
        )
        assert job.title == "Python Developer"
        assert job.match_score is None  # not set initially


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 