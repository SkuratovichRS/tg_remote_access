from unittest.mock import ANY, AsyncMock, call, patch


def test_api_execute(app_client):
    db_mock = AsyncMock()
    rabbit_mock = AsyncMock()
    with patch("app.api.api.get_db", return_value=db_mock):
        with patch("app.api.api.get_rabbit", return_value=rabbit_mock):
            r = app_client.post("/api/v1/execute/", json={"command": "ls"})
    assert r.status_code == 201
    assert r.json() == {"command": "ls", "command_id": ANY}
    assert db_mock.write_new_command.await_args_list == [call("ls", ANY)]
    assert rabbit_mock.producer_cmd.await_args_list == [call("ls", ANY)]
