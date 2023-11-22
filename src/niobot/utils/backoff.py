import asyncio
import logging
import random
import typing
import time
import functools


__all_ = (
    "ExponentialBackoff",

)


class ExponentialBackoff:
    """
    An exponential backoff iterator.

    This context manager can be used as both a regular Context Manager and an Async Context Manager.
    """
    def __init__(
            self,
            base_delay: float = 1.0,
            max_delay: float = 300.0,
            factor: float = 2.0,
            max_retries: int = 10,
            *,
            jitter: bool = False,
            log: typing.Optional[typing.Union[str, logging.Logger]] = None
    ):
        """
        :param base_delay: The base (minimum/starting/etc.) delay, in seconds. Defaults to 1 second.
        :param max_delay: The maximum delay, in seconds. Defaults to 5 minutes.
        :param factor: The factor to multiply by. Defaults to 2.0.
        :param max_retries: The maximum number of retries before raising StopIteration. Defaults to 10.
        :param jitter: Whether to add jitter to the delay. Defaults to False.
        :param log: The logger to use. Defaults to a logger named `niobot.utils.backoff`.
        """
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.factor = factor
        self.max_retries = max_retries
        self.jitter = jitter
        if log:
            if isinstance(log, str):
                self.log = logging.getLogger(log)
            else:
                self.log = log
        else:
            self.log = logging.getLogger(__name__)

        self.__retries = 0

    @property
    def retries(self) -> int:
        return self.__retries

    def reset(self):
        """Resets the current retry count to zero."""
        self.log.debug("Reset backoff retries to zero (from %d)", self.__retries)
        self.__retries = 0

    @property
    def delay(self) -> float:
        """Calculates the current delay based on the current retry count."""
        value = self.base_delay * (self.factor ** self.__retries)
        if self.jitter:
            value += random.uniform(0, value / 2)

        normalised = min(value, self.max_delay)
        self.log.debug(
            "Current delay: %.2f seconds (%.1f base delay * (%.1f factor ** %d retries))",
            normalised,
            self.base_delay,
            self.factor,
            self.__retries
        )
        return normalised

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.reset()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.reset()

    def __aiter__(self):
        return self

    def __iter__(self):
        return self

    async def __anext__(self):
        if self.__retries >= self.max_retries:
            raise StopAsyncIteration

        self.log.debug("Sleeping for %.2f seconds", self.delay)
        await asyncio.sleep(self.delay)
        self.__retries += 1
        return self

    def __next__(self):
        if self.__retries >= self.max_retries:
            raise StopIteration

        self.log.debug("Sleeping for %.2f seconds", self.delay)
        time.sleep(self.delay)
        self.__retries += 1
        return self
