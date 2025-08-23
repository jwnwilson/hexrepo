import pytest

from apps.aipet.agents.aipet_agent import (
    AipetAgent,
    PetActionRecommendation,
    PetNeeds,
    RecommendedAction,
)
from config import config  # noqa: E402


class TestPetNeeds:
    """Test PetNeeds model validation."""

    def test_valid_pet_needs(self):
        """Test creating valid PetNeeds."""
        needs = PetNeeds(hungry=50, tiredness=30, boredom=40, toilet=20)
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
            estimated_effect=80,
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
            estimated_effect=80,
        )

        secondary_action = RecommendedAction(
            action="Give water",
            priority=3,
            reasoning="Pet might also be thirsty",
            target_need="hungry",
            estimated_effect=40,
        )

        recommendation = PetActionRecommendation(
            primary_action=primary_action,
            secondary_actions=[secondary_action],
            overall_health_score=60,
            urgent_needs=["hungry"],
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
        return AipetAgent()

    def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert agent.model == config.AI_DEFAULT_MODEL
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
