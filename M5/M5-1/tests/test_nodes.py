import pytest
from task_fsm.nodes import NavigateTo, SpeakTTS
from task_fsm.context import TaskContext

def test_navigate_mock_fail():
    ctx = TaskContext(task_id="t1")
    node = NavigateTo("nav", {"pose": {"x":0}, "_mock": "fail"}, ctx)
    assert node.execute() == "FAILED"

def test_navigate_success():
    ctx = TaskContext(task_id="t1")
    node = NavigateTo("nav", {"pose": {"x":0}}, ctx)
    assert node.execute() == "SUCCESS"
    assert ctx.data["last_nav_result"] == {"x":0}