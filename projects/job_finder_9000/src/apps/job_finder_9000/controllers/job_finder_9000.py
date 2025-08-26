from django.contrib.auth import get_user_model
from ninja import ModelSchema
from ninja_extra import (
    ModelConfig,
    ModelControllerBase,
    ModelSchemaConfig,
    api_controller,
)
from ninja_extra.permissions import BasePermission, IsAuthenticated

from ..models import Job_finder_9000


class PetSchema(ModelSchema):
    class Config:
        model = Job_finder_9000
        model_fields = ["name", "description"]


class IsAdmin(BasePermission):
    def has_permission(self, request, controller):
        return request.user.is_staff


@api_controller(
    "/job_finder_9000", permissions=[IsAuthenticated, IsAdmin], tags=["Job_finder_9000"]
)
class Job_finder_9000Controller(ModelControllerBase):
    user_model = get_user_model()
    model_config = ModelConfig(
        model=Job_finder_9000,
        schema_config=ModelSchemaConfig(
            read_only_fields=["id", "created_at", "updated_at"]
        ),
    )
