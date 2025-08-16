import pytest
from unittest.mock import AsyncMock, patch
from apps.aipet.agents.aipet_agent import (
    AipetAgent, 
    PetNeeds, 
    RecommendedAction, 
    PetActionRecommendation
)


class TestPetNeeds:
    """Test PetNeeds model validation."""
    
    def test_valid_pet_needs(self):
        """Test creating valid PetNeeds."""
        needs = PetNeeds(
            hungry=50,
            tiredness=30,
            boredom=40,
            toilet=20
        )
        assert needs.hungry == 50
        assert needs.tiredness == 30
        assert needs.boredom == 40
        assert needs.toilet == 20
    
    def test_invalid_pet_needs(self):
        """Test PetNeeds validation with invalid values."""
        with pytest.raises(ValueError):
            PetNeeds(hungry=150, tiredness=30, boredom=40, toilet=20)
        
        with pytest.raises(ValueError):
            PetNeeds(hungry=-10, tiredness=30, boredom=40, toilet=20)


class TestRecommendedAction:
    """Test RecommendedAction model."""
    
    def test_valid_recommended_action(self):
        """Test creating valid RecommendedAction."""
        action = RecommendedAction(
            action="Feed the pet",
            priority=5,
            reasoning="Pet is very hungry",
            target_need="hungry",
            estimated_effect=80
        )
        assert action.action == "Feed the pet"
        assert action.priority == 5
        assert action.reasoning == "Pet is very hungry"
        assert action.target_need == "hungry"
        assert action.estimated_effect == 80


class TestPetActionRecommendation:
    """Test PetActionRecommendation model."""
    
    def test_valid_recommendation(self):
        """Test creating valid PetActionRecommendation."""
        primary_action = RecommendedAction(
            action="Feed the pet",
            priority=5,
            reasoning="Pet is very hungry",
            target_need="hungry",
            estimated_effect=80
        )
        
        secondary_action = RecommendedAction(
            action="Give water",
            priority=3,
            reasoning="Pet might also be thirsty",
            target_need="hungry",
            estimated_effect=40
        )
        
        recommendation = PetActionRecommendation(
            primary_action=primary_action,
            secondary_actions=[secondary_action],
            overall_health_score=60,
            urgent_needs=["hungry"]
        )
        
        assert recommendation.primary_action == primary_action
        assert len(recommendation.secondary_actions) == 1
        assert recommendation.overall_health_score == 60
        assert recommendation.urgent_needs == ["hungry"]


class TestAipetAgent:
    """Test AipetAgent functionality."""
    
    @pytest.fixture
    def agent(self):
        """Create an AipetAgent instance for testing."""
        return AipetAgent(model="test-model")
    
    def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert agent.model == "test-model"
        assert agent.agent is not None
    
    def test_system_message(self, agent):
        """Test system message contains expected content."""
        system_message = agent._get_system_message()
        assert "expert pet care AI assistant" in system_message
        assert "hungry" in system_message
        assert "tiredness" in system_message
        assert "boredom" in system_message
        assert "toilet" in system_message
    
    def test_format_needs_message(self, agent):
        """Test formatting of needs message."""
        pet_needs = PetNeeds(hungry=80, tiredness=30, boredom=40, toilet=20)
        message = agent._format_needs_message(pet_needs)
        
        assert "Hunger: 80/100" in message
        assert "Tiredness: 30/100" in message
        assert "Boredom: 40/100" in message
        assert "Toilet: 20/100" in message
    
    def test_fallback_recommendation_hungry(self, agent):
        """Test fallback recommendation for hungry pet."""
        pet_needs = PetNeeds(hungry=90, tiredness=30, boredom=40, toilet=20)
        recommendation = agent._get_fallback_recommendation(pet_needs)
        
        assert recommendation.primary_action.target_need == "hungry"
        assert "Feed" in recommendation.primary_action.action
        assert recommendation.primary_action.priority == 5
        assert "hungry" in recommendation.urgent_needs
    
    def test_fallback_recommendation_toilet(self, agent):
        """Test fallback recommendation for toilet need."""
        pet_needs = PetNeeds(hungry=30, tiredness=30, boredom=40, toilet=95)
        recommendation = agent._get_fallback_recommendation(pet_needs)
        
        assert recommendation.primary_action.target_need == "toilet"
        assert "outside" in recommendation.primary_action.action or "toilet" in recommendation.primary_action.action
        assert recommendation.primary_action.priority == 5
        assert "toilet" in recommendation.urgent_needs
    
    def test_fallback_recommendation_tiredness(self, agent):
        """Test fallback recommendation for tired pet."""
        pet_needs = PetNeeds(hungry=30, tiredness=85, boredom=40, toilet=20)
        recommendation = agent._get_fallback_recommendation(pet_needs)
        
        assert recommendation.primary_action.target_need == "tiredness"
        assert "rest" in recommendation.primary_action.action
        assert recommendation.primary_action.priority == 4
        assert "tiredness" in recommendation.urgent_needs
    
    def test_fallback_recommendation_boredom(self, agent):
        """Test fallback recommendation for bored pet."""
        pet_needs = PetNeeds(hungry=30, tiredness=30, boredom=70, toilet=20)
        recommendation = agent._get_fallback_recommendation(pet_needs)
        
        assert recommendation.primary_action.target_need == "boredom"
        assert "Play" in recommendation.primary_action.action
        assert recommendation.primary_action.priority == 3
    
    def test_overall_health_score_calculation(self, agent):
        """Test overall health score calculation."""
        pet_needs = PetNeeds(hungry=50, tiredness=50, boredom=50, toilet=50)
        recommendation = agent._get_fallback_recommendation(pet_needs)
        
        # With all needs at 50, health score should be 50
        assert recommendation.overall_health_score == 50
    
    @pytest.mark.asyncio
    @patch('apps.aipet.agents.aipet_agent.Agent')
    async def test_get_recommendations_success(self, mock_agent_class, agent):
        """Test successful recommendation generation."""
        # Mock the agent response
        mock_agent = AsyncMock()
        mock_agent.run.return_value = PetActionRecommendation(
            primary_action=RecommendedAction(
                action="Feed the pet",
                priority=5,
                reasoning="Pet is hungry",
                target_need="hungry",
                estimated_effect=80
            ),
            secondary_actions=[],
            overall_health_score=70,
            urgent_needs=["hungry"]
        )
        mock_agent_class.return_value = mock_agent
        
        # Test the method
        pet_needs = PetNeeds(hungry=80, tiredness=30, boredom=40, toilet=20)
        result = await agent.get_recommendations(pet_needs)
        
        assert result.primary_action.action == "Feed the pet"
        assert result.overall_health_score == 70
        assert "hungry" in result.urgent_needs
    
    @pytest.mark.asyncio
    @patch('apps.aipet.agents.aipet_agent.Agent')
    async def test_get_recommendations_fallback(self, mock_agent_class, agent):
        """Test fallback when AI agent fails."""
        # Mock the agent to raise an exception
        mock_agent = AsyncMock()
        mock_agent.run.side_effect = Exception("AI service unavailable")
        mock_agent_class.return_value = mock_agent
        
        # Test the method
        pet_needs = PetNeeds(hungry=90, tiredness=30, boredom=40, toilet=20)
        result = await agent.get_recommendations(pet_needs)
        
        # Should return fallback recommendation
        assert result.primary_action.target_need == "hungry"
        assert "Feed" in result.primary_action.action
        assert "hungry" in result.urgent_needs 