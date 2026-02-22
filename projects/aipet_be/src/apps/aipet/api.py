from typing import Optional

import logfire
from ninja import Router

from apps.aipet.agents.aipet_agent import PetActionRecommendation
from config import config

from .services.aipet import AipetService, SceneData

# configure logfire
if config.LOGFIRE_WRITE_TOKEN:
    logfire.configure(token=config.LOGFIRE_WRITE_TOKEN)
logfire.instrument_pydantic_ai()

router = Router(
    tags=["Aipet"],
)


@router.post("/recommendations", auth=None)
async def get_pet_recommendations(
    request, scene_data: SceneData, model: Optional[str] = None
) -> PetActionRecommendation:
    """
    Get AI-powered recommendations for pet care based on current needs.

    This endpoint uses the pydantic_ai agent to analyze pet needs and provide
    intelligent recommendations for actions to take.
    """
    # Initialize the service with optional model override
    service = AipetService(model=model)

    # Get recommendations
    recommendations = await service.get_pet_recommendations(scene_data)

    return recommendations
