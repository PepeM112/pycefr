import threading
from queue import Queue

STORE_TTL_SECONDS = 120

EventValue = str | int | float | None
Event = dict[str, EventValue]


class ProgressStore:
    """Thread-safe store for streaming analysis progress to SSE clients."""

    def __init__(self) -> None:
        self._events: list[Event] = []
        self._subscribers: list[Queue[Event | None]] = []
        self._lock = threading.Lock()
        self._is_closed = False

    def emit(self, step: str, **kwargs: EventValue) -> None:
        event: Event = {"step": step, **kwargs}
        with self._lock:
            self._events.append(event)
            for q in self._subscribers:
                q.put(event)

    def close(self) -> None:
        with self._lock:
            self._is_closed = True
            for q in self._subscribers:
                q.put(None)

    def subscribe(self) -> tuple[list[Event], "Queue[Event | None]"]:
        with self._lock:
            q: Queue[Event | None] = Queue()
            if self._is_closed:
                for event in self._events:
                    q.put(event)
                q.put(None)
            else:
                self._subscribers.append(q)
            return list(self._events), q

    def unsubscribe(self, q: "Queue[Event | None]") -> None:
        with self._lock:
            try:
                self._subscribers.remove(q)
            except ValueError:
                pass


_stores: dict[int, ProgressStore] = {}
_stores_lock = threading.Lock()


def create_store(analysis_id: int) -> ProgressStore:
    with _stores_lock:
        store = ProgressStore()
        _stores[analysis_id] = store
        return store


def get_store(analysis_id: int) -> ProgressStore | None:
    with _stores_lock:
        return _stores.get(analysis_id)


def remove_store(analysis_id: int) -> None:
    with _stores_lock:
        _stores.pop(analysis_id, None)


def schedule_store_removal(analysis_id: int) -> None:
    timer = threading.Timer(STORE_TTL_SECONDS, remove_store, args=(analysis_id,))
    timer.daemon = True
    timer.start()
