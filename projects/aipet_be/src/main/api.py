from ninja_extra import NinjaExtraAPI
from ninja_extra.security import SessionAuth
from apps.aipet.controllers import AipetController
from apps.aipet.api import router as aipet_router

api = NinjaExtraAPI(
    title="AI Pet API",
    description="AI Pet",
    urls_namespace="aipet",
    auth=SessionAuth()
)

api.register_controllers(AipetController)
api.add_router("aipet", aipet_router)

