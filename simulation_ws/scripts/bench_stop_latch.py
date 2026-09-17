"""One-way stop latch for one bounded test invocation."""
def advance_latch(previous, reason, elapsed):
    return previous or reason or ('time_limit' if elapsed >= 20 else None)
