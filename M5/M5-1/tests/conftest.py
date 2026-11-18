import pytest


@pytest.fixture
def tmp_yaml(tmp_path):
    counter = {"n": 0}

    def _write(text):
        counter["n"] += 1
        p = tmp_path / f"tasks_{counter['n']}.yaml"
        p.write_text(text, encoding="utf-8")
        return str(p)

    return _write