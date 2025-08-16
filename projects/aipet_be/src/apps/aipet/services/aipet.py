from typing import Optional
import logging

from ..agents.aipet_agent import AipetAgent, PetNeeds, PetActionRecommendation

logger = logging.getLogger(__name__)


class AipetService:
    """Service layer for AI pet care recommendations."""
    
    def __init__(self, model: Optional[str] = None):
        self.agent = AipetAgent(model=model)
    
    async def get_pet_recommendations(
        self,
        hungry: int,
        tiredness: int,
        boredom: int,
        toilet: int
    ) -> PetActionRecommendation:
        """
        Get AI-powered recommendations for pet care based on current needs.
        
        Args:
            hungry: Hunger level (0-100)
            tiredness: Tiredness level (0-100)
            boredom: Boredom level (0-100)
            toilet: Toilet need level (0-100)
            
        Returns:
            PetActionRecommendation with AI-generated recommendations
        """
        try:
            # Create PetNeeds object
            pet_needs = PetNeeds(
                hungry=hungry,
                tiredness=tiredness,
                boredom=boredom,
                toilet=toilet
            )
            
            # Get recommendations from the AI agent
            recommendations = await self.agent.get_recommendations(pet_needs)
            
            logger.info(f"Generated recommendations for pet needs: {pet_needs}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in AipetService.get_pet_recommendations: {e}")
            raise
    
    async def get_pet_recommendations_from_dict(
        self,
        needs_data: dict
    ) -> PetActionRecommendation:
        """
        Get recommendations from a dictionary containing pet needs.
        
        Args:
            needs_data: Dictionary with keys: hungry, tiredness, boredom, toilet
            
        Returns:
            PetActionRecommendation with AI-generated recommendations
        """
        try:
            # Extract needs from dictionary
            hungry = needs_data.get("hungry", 0)
            tiredness = needs_data.get("tiredness", 0)
            boredom = needs_data.get("boredom", 0)
            toilet = needs_data.get("toilet", 0)
            
            return await self.get_pet_recommendations(
                hungry=hungry,
                tiredness=tiredness,
                boredom=boredom,
                toilet=toilet
            )
            
        except Exception as e:
            logger.error(f"Error in AipetService.get_pet_recommendations_from_dict: {e}")
            raise
