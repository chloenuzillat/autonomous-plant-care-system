"""Fan-out of server-initiated messages to connected WebSocket clients.

This is the one place in ``api/`` that pushes rather than answers, so it is
worth being explicit about what it is not: there is no topic, no subscription
filter and no delivery guarantee. Every connected client receives every message,
and a client that cannot keep up is disconnected rather than buffered.

Two constraints shape the design.

**Publishers are not on the event loop.** Every HTTP handler in ``app.py`` is a
plain ``def``, which FastAPI runs in a worker thread (see that module's
docstring for why). A worker thread cannot ``await`` a send, so
:meth:`Hub.publish` does not send anything -- it hands the message to the event
loop with ``call_soon_threadsafe`` and returns immediately. A single
:meth:`Hub.drain` task, started by the app's lifespan, does the actual sending.
That also means a slow client can never slow down a database write.

**A dead client must not break a write.** Sends happen away from the request
that triggered them, so a failed send has nobody to report to. Such a socket is
simply dropped from the set; the next ``/health`` or reconnect is how a client
finds out.
"""

import asyncio
import logging
from datetime import datetime
from itertools import count
from threading import Lock
from typing import Any, Dict, Optional, Set

from fastapi import WebSocket

logger = logging.getLogger(__name__)

# Matches the format the store stamps on readings, so a client parsing one
# timestamp can parse both.
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Pending messages allowed before publishing starts dropping. Readings arrive
# seconds apart at most, so reaching this means the drain task is wedged or
# every client is unreachable, and the useful response to both is to shed load
# rather than grow without bound.
MAX_PENDING = 256


class Hub:
    """Tracks live WebSocket clients and broadcasts envelopes to them."""

    def __init__(self) -> None:
        self._clients: Set[WebSocket] = set()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._queue: Optional[asyncio.Queue] = None
        # next(count()) is atomic in CPython, but the lock also makes the
        # sequence match publish order across worker threads rather than just
        # being unique.
        self._seq = count(1)
        self._seq_lock = Lock()

    # ------------------------------------------------------------- lifecycle

    def attach(self, loop: asyncio.AbstractEventLoop) -> None:
        """
        Bind the hub to the running event loop. Called from the app's lifespan.

        Until this happens :meth:`publish` is a no-op, which is what lets a test
        import the app and exercise a handler without a server running.
        """
        self._loop = loop
        self._queue = asyncio.Queue(maxsize=MAX_PENDING)

    def detach(self) -> None:
        """Release the loop. After this, publishing is a no-op again."""
        self._loop = None
        self._queue = None

    async def drain(self) -> None:
        """
        Send queued envelopes until cancelled. Run as a lifespan task.

        Cancellation is the normal way this ends, so it is allowed to propagate
        rather than being swallowed.
        """
        assert self._queue is not None, "attach() must run before drain()"

        while True:
            envelope = await self._queue.get()
            await self._send_to_all(envelope)

    # ----------------------------------------------------------- connections

    async def connect(self, client: WebSocket) -> None:
        """Accept the handshake and start sending this client broadcasts."""
        await client.accept()
        self._clients.add(client)
        logger.info("websocket client connected (%d now)", len(self._clients))

    def disconnect(self, client: WebSocket) -> None:
        """Stop sending to this client. Safe to call more than once."""
        self._clients.discard(client)
        logger.info("websocket client disconnected (%d left)", len(self._clients))

    @property
    def subscriber_count(self) -> int:
        """How many clients a message published right now would reach."""
        return len(self._clients)

    # -------------------------------------------------------------- publishing

    def publish(self, message_type: str, **payload: Any) -> Optional[Dict[str, Any]]:
        """
        Queue one envelope for every connected client.

        Safe to call from any thread, which is the point: the callers are sync
        request handlers running in FastAPI's worker threads.

        :param message_type: Goes in the envelope's ``type``, and tells the
            client which payload key to read.
        :param payload: Merged into the envelope as-is, e.g. ``reading=row``.
        :return: The envelope as sent, or ``None`` if there was nothing to send
            it to and nothing was queued.
        """
        loop, queue = self._loop, self._queue
        if loop is None or queue is None:
            # No server running. Not an error: the write that triggered this
            # still succeeded, and there is nobody to tell.
            return None

        envelope = self._envelope(message_type, payload)

        # Hop to the loop thread, because asyncio.Queue is not thread-safe.
        loop.call_soon_threadsafe(self._enqueue, queue, envelope)

        return envelope

    async def send_to(self, client: WebSocket, message_type: str, **payload: Any) -> None:
        """Send one envelope to one client, for per-connection replies."""
        await client.send_json(self._envelope(message_type, payload))

    # ---------------------------------------------------------------- internals

    def _envelope(self, message_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Stamped at publish time, not send time, so seq reflects the order
        # things actually happened in rather than the order they drained.
        with self._seq_lock:
            seq = next(self._seq)

        return {
            "type": message_type,
            "seq": seq,
            "sent_at": datetime.now().strftime(TIME_FORMAT),
            **payload,
        }

    @staticmethod
    def _enqueue(queue: "asyncio.Queue", envelope: Dict[str, Any]) -> None:
        try:
            queue.put_nowait(envelope)
        except asyncio.QueueFull:
            # Dropping the newest is the cheap choice and the right one here:
            # the alternative is unbounded memory while nothing is draining.
            logger.warning(
                "websocket queue full, dropped %s seq=%s",
                envelope.get("type"),
                envelope.get("seq"),
            )

    async def _send_to_all(self, envelope: Dict[str, Any]) -> None:
        # Snapshot first: a send that fails mutates the set.
        for client in list(self._clients):
            try:
                await client.send_json(envelope)
            except Exception as exc:  # noqa: BLE001 - any failure means "gone"
                logger.info("dropping unreachable websocket client: %s", exc)
                self.disconnect(client)
