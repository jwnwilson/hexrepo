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
):
    """
    Get AI-powered recommendations for pet care based on current needs.
    
    This endpoint uses the pydantic_ai agent to analyze pet needs and provide
    intelligent recommendations for actions to take.
    """
    try:
        # Initialize the service with optional model override
        service = AipetService(model=model)
        
        # Get recommendations
        recommendations = await service.get_pet_recommendations(
            hungry=pet_needs.hungry,
            tiredness=pet_needs.tiredness,
            boredom=pet_needs.boredom,
            toilet=pet_needs.toilet
        )
        
        return recommendations.model_dump()
        
    except Exception as e:
        raise HttpError(500, f"Error getting pet recommendations: {str(e)}")


@router.post("/recommendations/dict", auth=[SessionAuthAsync(), JWTAuthAsync()])
async def get_pet_recommendations_from_dict(
    request,
    needs_data: dict,
    model: Optional[str] = None
):
    """
    Get AI-powered recommendations for pet care from a dictionary of needs.
    
    Alternative endpoint that accepts a dictionary instead of structured data.
    """
    try:
        # Initialize the service with optional model override
        service = AipetService(model=model)
        
        # Get recommendations from dictionary
        recommendations = await service.get_pet_recommendations_from_dict(needs_data)
        
        return recommendations.dict()
        
    except Exception as e:
        raise HttpError(500, f"Error getting pet recommendations: {str(e)}")
