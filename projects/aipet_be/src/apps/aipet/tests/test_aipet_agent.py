import pytest

from apps.aipet.agents.aipet_agent import (
    AipetAgent,
    PetNeeds,
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
        assert "You are an AI Pet" in system_message
        assert "hungry" in system_message
        assert "tiredness" in system_message
        assert "boredom" in system_message
        assert "toilet" in system_message
