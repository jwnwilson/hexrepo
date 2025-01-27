from typing import Dict
from hexrepo_log.log import log_manager, setup_logger
from app.domain.user import get_user_data


def handler(event: Dict, context: Dict) -> Dict:
    setup_logger()

    with log_manager():
        access_token = event.get("authorizationToken")
        return get_user_data(access_token)
