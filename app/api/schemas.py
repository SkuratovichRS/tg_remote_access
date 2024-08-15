from typing import Optional

from pydantic import BaseModel


class ExecuteCommandRequest(BaseModel):
    command: str


class ExecuteCommandResponse(ExecuteCommandRequest):
    command_id: str


class Result(BaseModel):
    stdout: Optional[str]
    stderr: Optional[str]
    returncode: int


class GetStatusResponse(BaseModel):
    command_id: str
    status: str
    result: Result | None
