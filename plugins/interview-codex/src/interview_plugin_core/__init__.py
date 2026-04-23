"""Portable Socratic interview core extracted from Ouroboros."""

from interview_plugin_core.ambiguity import AmbiguityScorer
from interview_plugin_core.errors import ProviderError, ValidationError
from interview_plugin_core.interview import (
    InterviewEngine,
    InterviewRound,
    InterviewState,
    InterviewStatus,
)
from interview_plugin_core.provider import (
    CompletionConfig,
    CompletionResponse,
    LLMAdapter,
    Message,
    MessageRole,
    UsageInfo,
)

__all__ = [
    "AmbiguityScorer",
    "CompletionConfig",
    "CompletionResponse",
    "InterviewEngine",
    "InterviewRound",
    "InterviewState",
    "InterviewStatus",
    "LLMAdapter",
    "Message",
    "MessageRole",
    "ProviderError",
    "UsageInfo",
    "ValidationError",
]
