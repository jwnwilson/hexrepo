import logging
from typing import List, Literal, Tuple

import logfire
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.run import AgentRunResult

from config import config  # noqa: E402

logger = logging.getLogger(__name__)

Actions = Literal["feed", "play", "toilet", "sleep"]
ObjectTypes = Literal["pet", "food", "toy", "bed", "toilet", "other"]


# Request/Response models for pet recommendations
class SceneObject(BaseModel):
    type: ObjectTypes
    position: Tuple[float, float, float]


class PetData(SceneObject):
    type: ObjectTypes = "pet"
    hungry: float
    tiredness: float
    boredom: float
    toilet: float


class SceneData(BaseModel):
    scene_data: list[SceneObject]
    pet_data: PetData


class PetNeeds(BaseModel):
    """Pet needs data structure matching the frontend PetNeeds interface."""

    hungry: int = Field(
        ge=0, le=100, description="Hunger level 0-100 (100 = very hungry)"
    )
    tiredness: int = Field(
        ge=0, le=100, description="Tiredness level 0-100 (100 = very tired)"
    )
    boredom: int = Field(
        ge=0, le=100, description="Boredom level 0-100 (100 = very bored)"
    )
    toilet: int = Field(
        ge=0, le=100, description="Toilet need level 0-100 (100 = really needs to go)"
    )


class PetActionRecommendation(BaseModel):
    """Complete recommendation response for pet actions."""

    movement: List[float] = Field(
        description="Direction to move the pet as [x, y, z] coordinates",
        min_items=3,
        max_items=3,
    )
    action: Actions = Field(description="Action to take")
    reasoning: str = Field(description="Reasoning for the action")


class AipetAgent:
    """AI agent for processing pet needs and recommending actions."""

    def __init__(self, model: str | None = None):
        self.model = model or config.AI_DEFAULT_MODEL
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create the pydantic_ai agent with appropriate configuration."""
        if "gemini" in self.model:
            provider = GoogleProvider(api_key=config.GEMINI_API_KEY)
            model = GoogleModel(self.model, provider=provider)
        else:
            model = self.model
        agent = Agent(
            model=model,
            output_type=PetActionRecommendation,
            system_prompt=self._get_system_message(),
            retries=2,
            name="aipet",
        )

        return agent

    def _get_system_message(self) -> str:
        """Get the system message for the pet care agent."""
        return """You are an AI Pet. Your job is to analyze your needs, the scene around you and return a movement direction (vector of 3 numbers) and action to satisfy your needs.

Pet needs are provided on a scale of 0-100 where:
- 0 = need is fully satisfied
- 100 = need is critical and requires immediate attention

Available needs to monitor:
- hungry: Hunger level
- tiredness: Sleep/tiredness level  
- boredom: Need for stimulation/play
- toilet: Need to relieve themselves

You can only use a need if your (the pet) position is within 1 unit of the need object.

Available data to analyse:
- pet position: (x, y, z)
- objects in the scene for each need with a position (x, y, z)

When analyzing needs:
1. Prioritize urgent needs (50+ on the scale) then the highest need after that
2. Return a move vector from the pet's position to an object that will satisfy an urgent need
3. Return an action to take to satisfy the need
4. Provide reasoning for your actions from the pet's perspective
"""

    def _format_needs_message(self, scene_data: SceneData) -> str:
        """Format pet needs into a message for the AI agent."""
        msg = f"""Please analyze the following pet needs, it's position, the scene data and return movement vector and appropriate action:

Pet Needs:
- Hunger: {scene_data.pet_data.hungry}/100
- Tiredness: {scene_data.pet_data.tiredness}/100  
- Boredom: {scene_data.pet_data.boredom}/100
- Toilet: {scene_data.pet_data.toilet}/100

Pet Position:
- Position: {scene_data.pet_data.position}

Scene Data:
"""
        for obj in scene_data.scene_data:
            msg += f"- {obj.type}: {obj.position}\n"
        return msg

    async def get_recommendations(
        self, scene_data: SceneData
    ) -> PetActionRecommendation:
        """
        Get action recommendations based on pet needs.
        """
        with logfire.span("Getting pet recommendations"):
            try:
                logfire.info(
                    "Getting pet recommendations",
                    model=self.model,
                    scene_data=scene_data,
                )

                # Create a user message describing the pet's needs
                user_message = self._format_needs_message(scene_data)

                # Get recommendations from the agent
                response: AgentRunResult = await self.agent.run(user_message)
                recommendation: PetActionRecommendation = response.output

                logfire.info(
                    "Successfully generated recommendations",
                    recommendation=recommendation,
                )

                logger.info(f"Generated recommendations for pet needs: {scene_data}")
                return recommendation

            except Exception as e:
                logfire.error(
                    "Error getting pet recommendations",
                    error=str(e),
                    error_type=type(e).__name__,
                    scene_data=scene_data,
                )
                logger.error(f"Error getting pet recommendations: {e}")
                raise
