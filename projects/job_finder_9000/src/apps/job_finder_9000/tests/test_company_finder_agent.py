"""
Tests for the CompanyFinderAgent
"""

import pytest

from apps.job_finder_9000.domain.job_finder_agent import (
    CandidateProfile,
    CompanyFinderAgent,
    Location,
    Skill,
)


class TestCompanyFinderAgent:
    """Test cases for CompanyFinderAgent"""

    @pytest.fixture
    def agent(self):
        """Create a CompanyFinderAgent instance for testing"""
        return CompanyFinderAgent()

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

    def test_agent_initialization(self, agent):
        """Test that the agent initializes with the correct system prompt"""
        assert agent.system_prompt is not None
        assert "recruiter" in agent.system_prompt.lower()
        assert "highest paying companies" in agent.system_prompt.lower()
