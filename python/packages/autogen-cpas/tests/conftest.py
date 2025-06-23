import pytest

@pytest.fixture(autouse=True, scope="session")
def _ensure_autogen_core() -> None:
    try:
        import autogen_core  # noqa: F401
    except Exception:
        pytest.skip(
            "autogen_core unavailable; skipping CPAS tests", allow_module_level=True
        )

