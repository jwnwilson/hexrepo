
import os
from typing import List

AWS_ENV_VARS = [
    "AWS_ACCOUNT",
    "AWS_DEFAULT_REGION",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
]


def check_missing_env_vars(cloud_provider: str) -> List[str]:
    missing_envs = []
    if cloud_provider == "aws":
        for env in AWS_ENV_VARS:
            if env not in os.environ:
                missing_envs.append(env)
        
    return missing_envs