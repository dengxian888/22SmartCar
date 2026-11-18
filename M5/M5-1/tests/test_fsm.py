from task_fsm.core import TaskEngine

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