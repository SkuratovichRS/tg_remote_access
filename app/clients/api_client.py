import logging
import time
from typing import Any

import requests

logger = logging.getLogger(__name__)


class ApiClient:
    def __init__(self, api_host: str):
        self._post_url = f"{api_host}/api/v1/execute/"
        self._get_url = f"{api_host}/api/v1/result/"
        self._timeout = 10

    def execute(self, command: str) -> Any:
        cmd_id = self._post_cmd(command)
        while self._get_result(cmd_id).get("status") != "executed":
            time.sleep(1)
        return self._get_result(cmd_id)

    def _post_cmd(self, command: str) -> Any:
        body = {"command": command}
        response = requests.post(url=self._post_url, json=body, timeout=self._timeout)
        logger.info(response.status_code)
        cmd_id = response.json().get("command_id")
        return cmd_id

    def _get_result(self, cmd_id: str) -> Any:
        params = {"command_id": cmd_id}
        response = requests.get(url=self._get_url, params=params, timeout=self._timeout)
        logger.info(response.status_code)
        return response.json()
