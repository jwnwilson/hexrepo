from ninja import ModelSchema
from ninja_extra import (
    ModelConfig,
    ModelSchemaConfig,
    api_controller, 
    ModelControllerBase
)
from ninja_extra.permissions import IsAuthenticated, BasePermission
from django.contrib.auth import get_user_model
from ..models import Aipet


class PetSchema(ModelSchema):
    class Config:
        model = Aipet
        model_fields = ['name', 'description']


class IsAdmin(BasePermission):
    def has_permission(self, request, controller):
        return request.user.is_staff


@api_controller('/aipet', permissions=[IsAuthenticated, IsAdmin])
class AipetController(ModelControllerBase):
    user_model = get_user_model()
    model_config = ModelConfig(
        model=Aipet,
        schema_config=ModelSchemaConfig(
            read_only_fields=["id", "created_at", "updated_at"]  
        ),
    )

