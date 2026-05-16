"""
Retry Handler — Tenacity-based retry with exponential backoff.
"""

from __future__ import annotations

import asyncio
import functools
from collections.abc import Callable
from typing import Any, TypeVar

import structlog
from tenacity import (
    AsyncRetrying,
    RetryError,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = structlog.get_logger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def async_retry(
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 10.0,
    reraise: bool = True,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[F], F]:
    """Decorator: retry async functions with exponential backoff."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                async for attempt in AsyncRetrying(
                    stop=stop_after_attempt(max_attempts),
                    wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
                    retry=retry_if_exception_type(exceptions),
                    reraise=reraise,
                ):
                    with attempt:
                        return await func(*args, **kwargs)
            except RetryError as e:
                logger.error(
                    "All retry attempts exhausted",
                    function=func.__name__,
                    attempts=max_attempts,
                    error=str(e),
                )
                raise

        return wrapper  # type: ignore[return-value]

    return decorator


class RetryHandler:
    """Standalone retry handler for use without decorators."""

    def __init__(
        self,
        max_attempts: int = 3,
        min_wait: float = 1.0,
        max_wait: float = 10.0,
    ) -> None:
        self.max_attempts = max_attempts
        self.min_wait = min_wait
        self.max_wait = max_wait

    async def execute(self, coro_func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute a coroutine with retry logic."""
        last_error: Exception | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                return await coro_func(*args, **kwargs)
            except Exception as e:
                last_error = e
                wait_time = min(self.min_wait * (2 ** (attempt - 1)), self.max_wait)
                logger.warning(
                    "Retry attempt",
                    function=coro_func.__name__,
                    attempt=attempt,
                    max_attempts=self.max_attempts,
                    wait=wait_time,
                    error=str(e),
                )
                if attempt < self.max_attempts:
                    await asyncio.sleep(wait_time)
        raise last_error or RuntimeError("Retry exhausted")
