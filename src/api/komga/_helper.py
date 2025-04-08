import json
from typing import Optional

from httpx import Response

from src.model.komga.common import KomgaViolationError, KomgaMultipleViolationErrors, KomgaError


def handle_resp(resp: Response) -> Optional[json]:
    if resp.text:
        result = json.loads(resp.text)
    else:
        return None

    if "violations" in result:
        violations = [r for r in result["violations"]]
        if len(violations) == 1:
            raise KomgaViolationError(violations[0])
        else:
            raise KomgaMultipleViolationErrors(violations)
    elif "error" in result:
        raise KomgaError(result)

    return result
