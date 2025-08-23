from ninja.security import SessionAuth
from ninja_extra import NinjaExtraAPI
from ninja_jwt.authentication import JWTAuth

from apps.job_finder_9000.api import router as job_finder_9000_router
from apps.job_finder_9000.controllers import Job_finder_9000Controller
from apps.login.controllers.login import NinjaJWTController, SignupController

api = NinjaExtraAPI(
    title="AI Pet API",
    description="AI Pet",
    urls_namespace="job_finder_9000",
    auth=[SessionAuth(), JWTAuth()],
)

api.register_controllers(NinjaJWTController)
api.register_controllers(Job_finder_9000Controller)
api.register_controllers(SignupController)
api.add_router("job_finder_9000", job_finder_9000_router)
