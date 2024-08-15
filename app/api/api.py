import json
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Request

from app.api import schemas

router = APIRouter()


def get_db(request: Request) -> Any:
    return request.app.state.db


def get_rabbit(request: Request) -> Any:
    return request.app.state.rabbit


@router.post("/api/v1/execute/", response_model=schemas.ExecuteCommandResponse, status_code=201)
async def execute(request: Request, command: schemas.ExecuteCommandRequest) -> schemas.ExecuteCommandResponse:
    db = get_db(request)
    rabbit = get_rabbit(request)
    command_name = command.command
    command_id = str(uuid.uuid4())
    await rabbit.producer_cmd(command_name, command_id)
    await db.write_new_command(command_name, command_id)
    return schemas.ExecuteCommandResponse(command=command_name, command_id=command_id)


@router.get("/api/v1/result/", response_model=schemas.GetStatusResponse, status_code=200)
async def get_result(request: Request, command_id: str) -> schemas.GetStatusResponse:
    db = get_db(request)
    try:
        status, result = await db.get_status_and_result(command_id)
    except Exception as e:
        raise HTTPException(404, "command with such id does not exists") from e
    return schemas.GetStatusResponse(
        command_id=command_id, status=status, result=schemas.Result(**json.loads(result)) if result else None
    )
