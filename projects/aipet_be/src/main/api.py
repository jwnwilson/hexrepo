from ninja.security import SessionAuth
from ninja_extra import NinjaExtraAPI
from ninja_jwt.authentication import JWTAuth

from apps.aipet.api import router as aipet_router
from apps.aipet.controllers import AipetController
from apps.login.controllers.login import NinjaJWTController, SignupController

api = NinjaExtraAPI(
    title="AI Pet API",
    description="AI Pet",
    urls_namespace="aipet",
    auth=[SessionAuth(), JWTAuth()],
)

api.register_controllers(NinjaJWTController)
api.register_controllers(AipetController)
api.register_controllers(SignupController)
api.add_router("aipet", aipet_router)
