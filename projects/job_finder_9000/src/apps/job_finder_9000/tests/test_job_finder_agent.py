"""
Tests for the JobFinderAgent
"""

import pytest

from apps.job_finder_9000.domain.job_finder_agent import (
    CandidateProfile,
    CompanySearchResult,
    JobFinderAgent,
    Location,
    Skill,
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
                Skill(
                    name="JavaScript", proficiency="intermediate", years_experience=3
                ),
            ],
            experience_years=5,
            preferred_locations=[
                Location(
                    city="San Francisco",
                    state="CA",
                    country="USA",
                    remote_preference="hybrid",
                ),
                Location(
                    city="New York",
                    state="NY",
                    country="USA",
                    remote_preference="hybrid",
                ),
            ],
            salary_expectation=120000,
            job_preferences={"industry": "tech", "company_size": "startup"},
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
                reasoning="High-paying tech company",
            ),
            CompanySearchResult(
                company_name="Meta",
                location="Menlo Park, CA",
                industry="Technology",
                company_size="enterprise",
                average_salary=140000,
                hiring_status="active",
                remote_friendly=True,
                reasoning="Leading social media company",
            ),
        ]

    def test_agent_initialization(self, agent):
        """Test that the agent initializes with the correct system prompt"""
        assert agent.system_prompt is not None
        assert "recruiter" in agent.system_prompt.lower()
        assert "active job postings" in agent.system_prompt.lower()
        assert "company websites" in agent.system_prompt.lower()
