import logging
from typing import Literal, Optional, Tuple

from pydantic import BaseModel

from ..agents.aipet_agent import AipetAgent, PetActionRecommendation, PetNeeds

logger = logging.getLogger(__name__)


ObjectTypes = Literal["pet", "food", "toy", "bed", "toilet", "other"]

# Request/Response models for pet recommendations
class SceneObject(BaseModel):
    type: ObjectTypes
    position: Tuple[float, float, float]


class PetData(SceneObject):
    type: ObjectTypes = "pet"
    hungry: int
    tiredness: int
    boredom: int
    toilet: int


class SceneData(BaseModel):
    scene_data: list[SceneObject]
    pet_data: PetData


class AipetService:
    """Service layer for AI pet care recommendations."""

    def __init__(self, model: Optional[str] = None):
        self.agent = AipetAgent(model=model)

    async def get_pet_recommendations(
        self, scene_data: SceneData
    ) -> PetActionRecommendation:
        """
        Get AI-powered recommendations for pet care based on current needs.
        """
        try:
            # Get recommendations from the AI agent
            recommendations = await self.agent.get_recommendations(scene_data)

            logger.info(f"Generated recommendations for scene_data: {scene_data}")
            return recommendations

        except Exception as e:
            logger.error(f"Error in AipetService.get_pet_recommendations: {e}")
            raise
