from __future__ import annotations

import pandas as pd
import pytest

from spark_insights.analysis import analyze
from spark_insights.contracts import TaskSpec
from spark_insights.providers import NarrationRequest, ProviderError, narrate


class FakeClient:
    def generate(self, *, model: str, api_key: str, prompt: str) -> str:
        assert model == "custom-model"
        assert api_key == "session-key"
        assert "Validated result JSON" in prompt
        return "Grounded narration"


class ExplodingClient:
    def generate(self, *, model: str, api_key: str, prompt: str) -> str:
        raise RuntimeError(f"secret SDK detail: {api_key}")


class EmptyClient:
    def generate(self, *, model: str, api_key: str, prompt: str) -> str:
        return ""


def test_cloud_requires_explicit_consent_and_key() -> None:
    result = analyze(pd.DataFrame({"x": [1, 2]}), TaskSpec())
    with pytest.raises(ValueError, match="consent"):
        narrate(
            result,
            NarrationRequest("gemini", "custom-model", "session-key", False),
            client=FakeClient(),
        )
    with pytest.raises(ValueError, match="API key"):
        narrate(result, NarrationRequest("gemini", "custom-model", "", True), client=FakeClient())
    assert (
        narrate(
            result,
            NarrationRequest("gemini", "custom-model", "session-key", True),
            client=FakeClient(),
        )
        == "Grounded narration"
    )


def test_provider_errors_are_stable_and_redacted() -> None:
    result = analyze(pd.DataFrame({"x": [1, 2]}), TaskSpec())
    with pytest.raises(ProviderError) as caught:
        narrate(
            result,
            NarrationRequest("openai", "custom-model", "never-print-me", True),
            client=ExplodingClient(),
        )
    assert str(caught.value) == "Cloud narration request failed"
    assert caught.value.__cause__ is None
    with pytest.raises(ProviderError, match="Cloud narration request failed"):
        narrate(
            result,
            NarrationRequest("openai", "custom-model", "session-key", True),
            client=EmptyClient(),
        )
