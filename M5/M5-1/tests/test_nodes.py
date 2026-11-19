import pytest
import time
import threading
from task_fsm.nodes import WaitForTrigger, SpeakTTS, NavigateTo
from task_fsm.context import TaskContext

@pytest.fixture
def ctx():
    return TaskContext(task_id="node_test")

# ================= 测试 WaitForTrigger =================
def test_wait_trigger_success(ctx):
    """用例1：正常触发成功"""
    node = WaitForTrigger("w1", {"_mock_trigger_after": 0.05}, ctx)
    start = time.monotonic()
    assert node.execute() == "SUCCESS"
    assert time.monotonic() - start >= 0.05

def test_wait_trigger_no_source(ctx):
    """用例2：未配置触发源，直接失败"""
    node = WaitForTrigger("w2", {}, ctx)
    assert node.execute() == "FAILED"

def test_wait_trigger_cancelled(ctx):
    """用例3：执行过程中被手动 cancel 取消"""
    node = WaitForTrigger("w3", {"_mock_trigger_after": 10}, ctx)
    
    # 开一个定时器，0.1秒后触发取消
    timer = threading.Timer(0.1, node.cancel)
    timer.start()
    
    start = time.monotonic()
    result = node.execute()
    timer.cancel()
    
    assert result == "CANCELLED"
    assert time.monotonic() - start < 1.0 # 证明没有等10秒，而是提前退出了


# ================= 测试 SpeakTTS =================
def test_tts_success(ctx):
    """用例1：正常播报"""
    node = SpeakTTS("tts1", {"text": "测试语音"}, ctx)
    assert node.execute() == "SUCCESS"

def test_tts_empty_text(ctx):
    """用例2：空文本也能安全执行"""
    node = SpeakTTS("tts2", {}, ctx)
    assert node.execute() == "SUCCESS"

def test_tts_mock_fail(ctx):
    """用例3：模拟硬件/驱动失败"""
    node = SpeakTTS("tts3", {"_mock": "fail"}, ctx)
    assert node.execute() == "FAILED"


# ================= 测试 NavigateTo (顺带补齐) =================
def test_nav_no_pose(ctx):
    """用例1：没给目标点直接失败"""
    node = NavigateTo("nav1", {}, ctx)
    assert node.execute() == "FAILED"

def test_nav_mock_fail(ctx):
    """用例2：模拟导航失败"""
    node = NavigateTo("nav2", {"pose": {"x":0}, "_mock": "fail"}, ctx)
    assert node.execute() == "FAILED"

def test_nav_success(ctx):
    """用例3：正常到达，验证上下文写入"""
    node = NavigateTo("nav3", {"pose": {"x":10, "y":5}}, ctx)
    assert node.execute() == "SUCCESS"
    assert ctx.data["last_nav_result"] == {"x":10, "y":5}