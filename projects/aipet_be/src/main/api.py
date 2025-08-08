from ninja_extra import NinjaExtraAPI
from ninja.security import SessionAuth
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.controller import NinjaJWTDefaultController
from apps.aipet.controllers import AipetController
from apps.aipet.api import router as aipet_router

api = NinjaExtraAPI(
    title="AI Pet API",
    description="AI Pet",
    urls_namespace="aipet",
    auth=[SessionAuth(), JWTAuth()]
)

api.register_controllers(NinjaJWTDefaultController)
api.register_controllers(AipetController)
api.add_router("aipet", aipet_router)

