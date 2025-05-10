from typing import TYPE_CHECKING

import jinja2

from hextech.domain.project import find_repo_root

if TYPE_CHECKING:
    from hextech.domain.config import HexrepoConfig

