from typing import List
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
import logging

from config import config

logger = logging.getLogger(__name__)


class PetNeeds(BaseModel):
    """Pet needs data structure matching the frontend PetNeeds interface."""
    hungry: int = Field(ge=0, le=100, description="Hunger level 0-100 (100 = very hungry)")
    tiredness: int = Field(ge=0, le=100, description="Tiredness level 0-100 (100 = very tired)")
    boredom: int = Field(ge=0, le=100, description="Boredom level 0-100 (100 = very bored)")
    toilet: int = Field(ge=0, le=100, description="Toilet need level 0-100 (100 = really needs to go)")


class RecommendedAction(BaseModel):
    """Recommended action for the pet based on its needs."""
    action: str = Field(description="The recommended action to take")
    priority: int = Field(ge=1, le=5, description="Priority level 1-5 (5 = highest priority)")
    reasoning: str = Field(description="Explanation of why this action is recommended")
    target_need: str = Field(description="Which need this action addresses")
    estimated_effect: int = Field(ge=0, le=100, description="Estimated effect on the need (0-100)")


class PetActionRecommendation(BaseModel):
    """Complete recommendation response for pet actions."""
    primary_action: RecommendedAction = Field(description="The most important action to take")
    secondary_actions: List[RecommendedAction] = Field(description="Additional actions to consider")
    overall_health_score: int = Field(ge=0, le=100, description="Overall pet health score based on needs")
    urgent_needs: List[str] = Field(description="List of needs that require immediate attention")


class AipetAgent:
    """AI agent for processing pet needs and recommending actions."""
    
    def __init__(self, model: str = config.OPENROUTER_DEFAULT_MODEL):
        self.model = model
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the pydantic_ai agent with appropriate configuration."""
        model = OpenAIModel(
            self.model,  # or any other OpenRouter model
            base_url="https://openrouter.ai/api/v1",
            api_key=config.OPENROUTER_API_KEY,
        )
        
        return Agent(
            model=model,
            output_type=PetActionRecommendation,
            system_prompt=self._get_system_message(),
            retries=2
        )
    
    def _get_system_message(self) -> str:
        """Get the system message for the pet care agent."""
        return """You are an expert pet care AI assistant. Your job is to analyze a pet's needs and recommend appropriate actions.

Pet needs are provided on a scale of 0-100 where:
- 0 = need is fully satisfied
- 100 = need is critical and requires immediate attention

Available needs to monitor:
- hungry: Hunger level
- tiredness: Sleep/tiredness level  
- boredom: Need for stimulation/play
- toilet: Need to relieve themselves

When analyzing needs:
1. Prioritize urgent needs (80+ on the scale)
2. Consider the pet's overall well-being
3. Recommend specific, actionable steps
4. Provide reasoning for your recommendations
5. Estimate the effectiveness of each action

Available actions you can recommend:
- Feed the pet (addresses hunger)
- Give water (addresses thirst/hunger)
- Play with toys (addresses boredom)
- Take for a walk (addresses exercise, boredom, toilet)
- Let outside/toilet (addresses toilet needs)
- Provide rest/sleep area (addresses tiredness)
- Groom the pet (addresses boredom, bonding)
- Training session (addresses boredom, mental stimulation)

Always provide a primary action (highest priority) and secondary actions (additional considerations)."""
    
    async def get_recommendations(self, pet_needs: PetNeeds) -> PetActionRecommendation:
        """
        Get action recommendations based on pet needs.
        
        Args:
            pet_needs: PetNeeds object containing the current need levels
            
        Returns:
            PetActionRecommendation with primary and secondary actions
        """
        try:
            # Create a user message describing the pet's needs
            user_message = self._format_needs_message(pet_needs)
            
            # Get recommendations from the agent
            response = await self.agent.run(user_message)
            
            logger.info(f"Generated recommendations for pet needs: {pet_needs}")
            return response
            
        except Exception as e:
            logger.error(f"Error getting pet recommendations: {e}")
            # Return a fallback recommendation
            return self._get_fallback_recommendation(pet_needs)
    
    def _format_needs_message(self, pet_needs: PetNeeds) -> str:
        """Format pet needs into a message for the AI agent."""
        return f"""Please analyze the following pet needs and recommend appropriate actions:

Current Pet Needs:
- Hunger: {pet_needs.hungry}/100
- Tiredness: {pet_needs.tiredness}/100  
- Boredom: {pet_needs.boredom}/100
- Toilet: {pet_needs.toilet}/100

Please provide a comprehensive recommendation including:
1. Primary action (most urgent need)
2. Secondary actions (additional considerations)
3. Overall health assessment
4. Any urgent needs requiring immediate attention"""
    
    def _get_fallback_recommendation(self, pet_needs: PetNeeds) -> PetActionRecommendation:
        """Provide a fallback recommendation if the AI agent fails."""
        # Simple logic to determine the most urgent need
        needs_dict = {
            "hungry": pet_needs.hungry,
            "tiredness": pet_needs.tiredness,
            "boredom": pet_needs.boredom,
            "toilet": pet_needs.toilet
        }
        
        most_urgent_need = max(needs_dict, key=needs_dict.get)
        urgent_value = needs_dict[most_urgent_need]
        
        # Create fallback actions based on the most urgent need
        if most_urgent_need == "hungry":
            primary_action = RecommendedAction(
                action="Feed the pet immediately",
                priority=5 if urgent_value > 80 else 4,
                reasoning=f"Pet is very hungry ({urgent_value}/100) and needs food",
                target_need="hungry",
                estimated_effect=80
            )
        elif most_urgent_need == "toilet":
            primary_action = RecommendedAction(
                action="Take pet outside or to designated toilet area",
                priority=5 if urgent_value > 80 else 4,
                reasoning=f"Pet urgently needs to relieve themselves ({urgent_value}/100)",
                target_need="toilet",
                estimated_effect=90
            )
        elif most_urgent_need == "tiredness":
            primary_action = RecommendedAction(
                action="Provide a quiet rest area for the pet",
                priority=4 if urgent_value > 70 else 3,
                reasoning=f"Pet is tired ({urgent_value}/100) and needs rest",
                target_need="tiredness",
                estimated_effect=70
            )
        else:  # boredom
            primary_action = RecommendedAction(
                action="Play with the pet using toys or interactive games",
                priority=3 if urgent_value > 60 else 2,
                reasoning=f"Pet is bored ({urgent_value}/100) and needs stimulation",
                target_need="boredom",
                estimated_effect=60
            )
        
        # Calculate overall health score
        overall_health = 100 - (sum(needs_dict.values()) / len(needs_dict))
        
        # Identify urgent needs
        urgent_needs = [need for need, value in needs_dict.items() if value > 80]
        
        return PetActionRecommendation(
            primary_action=primary_action,
            secondary_actions=[],
            overall_health_score=int(overall_health),
            urgent_needs=urgent_needs
        )
