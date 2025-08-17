from apps.aipet.agents.aipet_agent import PetActionRecommendation
from ninja import Router
from ninja.errors import HttpError
from typing import Optional
from pydantic import BaseModel

from apps.core.auth import SessionAuthAsync, JWTAuthAsync
from config import config
from .services.aipet import AipetService

router = Router(
    tags=["Aipet"],
)

# Request/Response models for pet recommendations
class PetNeedsRequest(BaseModel):
    hungry: int
    tiredness: int
    boredom: int
    toilet: int


@router.post("/recommendations", auth=[SessionAuthAsync(), JWTAuthAsync()])
async def get_pet_recommendations(
    request,
    pet_needs: PetNeedsRequest,
    model: Optional[str] = None
) -> PetActionRecommendation:
    """
    Get AI-powered recommendations for pet care based on current needs.
    
    This endpoint uses the pydantic_ai agent to analyze pet needs and provide
    intelligent recommendations for actions to take.
    """
    # Initialize the service with optional model override
    service = AipetService(model=model)
    
    # Get recommendations
    recommendations = await service.get_pet_recommendations(
        hungry=pet_needs.hungry,
        tiredness=pet_needs.tiredness,
        boredom=pet_needs.boredom,
        toilet=pet_needs.toilet
    )
    
    return recommendations
