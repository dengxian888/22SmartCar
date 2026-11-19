from task_fsm.core import TaskEngine
import time
from task_fsm.context import TaskContext

def test_retry_then_success(tmp_yaml):
    path = tmp_yaml("""
tasks:
  - name: nav
    type: NavigateTo
    pose: {x: 1, y: 0}
    retry: 2
    retry_interval: 0.0
    _mock: [fail, fail, success]
""")
    engine = TaskEngine(path)
    assert engine.run() == "SUCCESS"
    assert engine.ctx.meta["retries"]["nav"] == 2

def test_fallback_to_skip(tmp_yaml):
    path = tmp_yaml("""
tasks:
  - name: nav
    type: NavigateTo
    pose: {x: 1, y: 0}
    retry: 0
    fallback: detect
    on_fail: skip
    _mock: fail
  - name: detect
    type: DetectTarget
    min_confidence: 0.99
    _mock: fail
""")
    engine = TaskEngine(path)
    assert engine.run() == "SUCCESS"
    assert engine.ctx.degraded is True

def test_step_timeout(tmp_yaml):
    path = tmp_yaml("""
tasks:
  - name: slow_nav
    type: NavigateTo
    pose: {x: 1, y: 0}
    timeout: 0.1
    _mock_sleep: 10
    fallback: quick_tts
  - name: quick_tts
    type: SpeakTTS
    text: "降级"
""")
    engine = TaskEngine(path)
    assert engine.run() == "SUCCESS"

def test_parallel_any_fail(tmp_yaml):
    path = tmp_yaml("""
tasks:
  - name: checks
    parallel:
      fail_policy: any_fail
      branches:
        - name: a
          type: NavigateTo
          pose: {x: 0, y: 0}
          _mock: fail
        - name: b
          type: SpeakTTS
""")
    engine = TaskEngine(path)
    assert engine.run() == "FAILED"

def test_yaml_unknown_type(tmp_yaml):
    import pytest
    path = tmp_yaml("""
tasks:
  - name: bad
    type: NotExist
""")
    with pytest.raises(ValueError, match="未知 type"):
        TaskEngine(path)
        
        
def test_wait_for_trigger_cancel(tmp_yaml):
    """测试取消语义：等待过程中被超时打断"""
    path = tmp_yaml("""
tasks:
  - name: wait_forever
    type: WaitForTrigger
    timeout: 0.1            # 0.1秒就超时取消
    _mock_trigger_after: 10 # 但模拟等10秒
""")
    engine = TaskEngine(path)
    # 因为超时了，所以应返回 FAILED 或 ABORTED
    assert engine.run() == "FAILED"
    # 验证记录里的状态被正确标记为超时取消
    assert any(s["status"] in ("FAILED", "ABORTED") for s in engine.steps)


def test_speak_tts_mock_fail(tmp_yaml):
    """测试 TTS 节点失败并走 on_fail: abort 的场景"""
    path = tmp_yaml("""
tasks:
  - name: speak
    type: SpeakTTS
    text: "hello"
    _mock: fail
""")
    engine = TaskEngine(path)
    assert engine.run() == "FAILED"


def test_task_deadline_timeout(tmp_yaml):
    """框架级：任务总时限 deadline 截断"""
    path = tmp_yaml("""
tasks:
  - name: sleep_task
    type: WaitForTrigger
    _mock_trigger_after: 0.2
  - name: next_task
    type: SpeakTTS
""")
    # 手动注入一个已经过期的 deadline
    ctx = TaskContext(task_id="test_deadline", deadline=time.monotonic() - 1)
    engine = TaskEngine(path, ctx=ctx)
    
    # 因为一开始就过了 deadline，引擎应该直接返回 TIMEOUT
    assert engine.run() == "TIMEOUT"
    # 验证后续任务没有被执行
    assert len(engine.steps) == 0