import logging
import logfire
from typing import Optional

from ..agents.aipet_agent import AipetAgent, PetActionRecommendation, SceneData

logger = logging.getLogger(__name__)


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
        with logfire.span("get_pet_recommendations"):
            try:
                # Get recommendations from the AI agent
                recommendations = await self.agent.get_recommendations(scene_data)

                logger.info(f"Generated recommendations for scene_data: {scene_data}")
                return recommendations

            except Exception as e:
                logger.error(f"Error in AipetService.get_pet_recommendations: {e}")
                raise
