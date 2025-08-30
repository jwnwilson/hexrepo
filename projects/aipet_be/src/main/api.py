from ninja.security import SessionAuth
from ninja_extra import NinjaExtraAPI
from ninja_jwt.authentication import JWTAuth

from apps.aipet.api import router as aipet_router
from apps.aipet.controllers import AipetController
from apps.core.controllers import CsrfController
from apps.login.controllers.login import NinjaJWTController, SignupController

api = NinjaExtraAPI(
    title="AI Pet API",
    description="AI Pet",
    urls_namespace="aipet",
    auth=[SessionAuth(), JWTAuth()],
)


# Healthcheck endpoint
@api.get("/health", auth=None)
def healthcheck(request):
    return {"status": "ok", "message": "AI Pet API"}


api.register_controllers(NinjaJWTController)
api.register_controllers(AipetController)
api.register_controllers(SignupController)
api.register_controllers(CsrfController)
api.add_router("aipet", aipet_router)
