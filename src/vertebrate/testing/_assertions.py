"""
Assertion helpers that don't depend on a test framework.
"""

import re
from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def raises(
    expected: type[BaseException] | tuple[type[BaseException], ...],
    match: str | None = None,
) -> Iterator[None]:
    """
    Assert that the block raises `expected`, optionally with a message
    matching the regular expression `match`.
    """
    try:
        yield
    except expected as error:
        if match is not None and not re.search(match, str(error)):
            msg = f"{type(error).__name__}({str(error)!r}) does not match {match!r}"
            raise AssertionError(msg) from error
        return
    raise AssertionError(f"Did not raise {expected!r}")
