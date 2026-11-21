"""FIFO order fulfillment queue using collections.deque (Step 2 extended)."""

from __future__ import annotations

from collections import deque


class FulfillmentQueue:
    """Dispatches paid orders in First-In, First-Out order."""

    def __init__(self) -> None:
        self._queue: deque[int] = deque()

    def enqueue(self, order_id: int) -> None:
        # SOLUTION_START
        self._queue.append(order_id)
        # SOLUTION_REPLACE
        # raise NotImplementedError("TODO: implementa enqueue en fulfillment.py")
        # SOLUTION_END

    def dequeue(self) -> int | None:
        # SOLUTION_START
        if not self._queue:
            return None
        return self._queue.popleft()
        # SOLUTION_REPLACE
        # raise NotImplementedError("TODO: implementa dequeue en fulfillment.py")
        # SOLUTION_END

    def pending_count(self) -> int:
        # SOLUTION_START
        return len(self._queue)
        # SOLUTION_REPLACE
        # raise NotImplementedError("TODO: implementa pending_count en fulfillment.py")
        # SOLUTION_END
