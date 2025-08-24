"""
Tests for the CompanyFinderAgent
"""

import pytest
from unittest.mock import AsyncMock, patch
from apps.job_finder_9000.domain.job_finder_agent import (
    CompanyFinderAgent,
    CompanySearchResponse,
    CompanySearchResult,
    CandidateProfile,
    Skill,
    Location
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
    
    def test_agent_initialization(self, agent):
        """Test that the agent initializes with the correct system prompt"""
        assert agent.system_prompt is not None
        assert "recruiter" in agent.system_prompt.lower()
        assert "highest paying companies" in agent.system_prompt.lower()
    
    @pytest.mark.asyncio
    async def test_search_companies_success(self, agent, sample_candidate):
        """Test successful company search with LLM response"""
        # Mock LLM response
        mock_response = CompanySearchResponse(
            companies=[
                CompanySearchResult(
                    company_name="Google",
                    location="Mountain View, CA",
                    industry="Technology",
                    company_size="enterprise",
                    average_salary=150000,
                    hiring_status="active",
                    remote_friendly=True,
                    reasoning="High-paying tech company in preferred location"
                ),
                CompanySearchResult(
                    company_name="Meta",
                    location="Menlo Park, CA",
                    industry="Technology",
                    company_size="enterprise",
                    average_salary=140000,
                    hiring_status="active",
                    remote_friendly=True,
                    reasoning="Leading social media company with competitive salaries"
                )
            ],
            search_criteria={},
            total_companies_found=2
        )
        
        company_agent_state = {
            "locations": ["San Francisco", "New York"],
            "keywords": ["Python", "JavaScript"],
            "candidate": sample_candidate,
            "include_remote": True,
            "max_results": 10
        }
        
        with patch.object(agent, 'ainvoke', new_callable=AsyncMock) as mock_ainvoke:
            mock_ainvoke.return_value = mock_response
            
            result = await agent.search_companies(company_agent_state)
            
            # Verify the result
            assert isinstance(result, CompanySearchResponse)
            assert len(result.companies) == 2
            assert result.companies[0].company_name == "Google"
            assert result.companies[1].company_name == "Meta"
            assert result.total_companies_found == 2
            
            # Verify LLM was called with correct parameters
            mock_ainvoke.assert_called_once()
            call_args = mock_ainvoke.call_args
            assert call_args[1]['response_model'] == CompanySearchResponse
            assert call_args[1]['system_prompt'] == agent.system_prompt
    
    @pytest.mark.asyncio
    async def test_search_companies_fallback_on_error(self, agent, sample_candidate):
        """Test fallback behavior when LLM call fails"""
        company_agent_state = {
            "locations": ["San Francisco"],
            "keywords": ["Python"],
            "candidate": sample_candidate,
            "include_remote": True,
            "max_results": 5
        }
        
        with patch.object(agent, 'ainvoke', new_callable=AsyncMock) as mock_ainvoke:
            mock_ainvoke.side_effect = Exception("LLM API error")
            
            result = await agent.search_companies(company_agent_state)
            
            # Verify fallback response
            assert isinstance(result, CompanySearchResponse)
            assert len(result.companies) == 1
            assert result.companies[0].company_name == "Tech Company A"
            assert result.companies[0].reasoning == "Fallback company due to LLM error"
            assert result.total_companies_found == 1
    
    @pytest.mark.asyncio
    async def test_search_companies_respects_max_results(self, agent, sample_candidate):
        """Test that the agent respects the max_results parameter"""
        # Mock response with more companies than max_results
        mock_companies = [
            CompanySearchResult(
                company_name=f"Company {i}",
                location="San Francisco, CA",
                industry="Technology",
                company_size="mid-size",
                average_salary=120000,
                hiring_status="active",
                remote_friendly=True,
                reasoning=f"Company {i} reasoning"
            )
            for i in range(15)  # More than max_results=10
        ]
        
        mock_response = CompanySearchResponse(
            companies=mock_companies,
            search_criteria={},
            total_companies_found=15
        )
        
        company_agent_state = {
            "locations": ["San Francisco"],
            "keywords": ["Python"],
            "candidate": sample_candidate,
            "include_remote": True,
            "max_results": 10
        }
        
        with patch.object(agent, 'ainvoke', new_callable=AsyncMock) as mock_ainvoke:
            mock_ainvoke.return_value = mock_response
            
            result = await agent.search_companies(company_agent_state)
            
            # Verify that only max_results companies are returned
            assert len(result.companies) == 10
            assert result.total_companies_found == 10
            assert result.companies[0].company_name == "Company 0"
            assert result.companies[9].company_name == "Company 9"
    
    def test_system_prompt_content(self, agent):
        """Test that the system prompt contains expected content"""
        prompt = agent.system_prompt.lower()
        
        # Check for key concepts
        assert "recruiter" in prompt
        assert "highest paying" in prompt
        assert "preferred location" in prompt
        assert "salary" in prompt
        assert "hiring" in prompt
        assert "remote" in prompt
        assert "hybrid" in prompt
        assert "on-site" in prompt 