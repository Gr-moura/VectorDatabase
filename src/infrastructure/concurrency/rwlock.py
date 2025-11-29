# src/infrastructure/concurrency/rwlock.py

import threading
from contextlib import contextmanager


class RWLock:
    """
    A simple Reader-Writer Lock implementation using Python's threading primitives.
    Allows multiple concurrent readers, but only one exclusive writer.
    Writer priority is not strictly enforced here to keep it simple, but
    writers will block new readers.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._readers_ok = threading.Condition(self._lock)
        self._writers_ok = threading.Condition(self._lock)

        self._num_readers = 0  # Active readers
        self._writer_active = False  # Is a writer currently writing?
        self._writers_waiting = 0  # Number of writers waiting

    @contextmanager
    def read_lock(self):
        """Context manager for acquiring a shared read lock."""
        with self._lock:
            # Wait until no writer is active
            while self._writer_active or self._writers_waiting > 0:
                self._writers_ok.wait()
            self._num_readers += 1

        try:
            yield

        finally:
            with self._lock:
                self._num_readers -= 1
                # If I was the last reader, notify waiting writers
                if self._num_readers == 0:
                    self._readers_ok.notify_all()

    @contextmanager
    def write_lock(self):
        """Context manager for acquiring an exclusive write lock."""
        with self._lock:
            self._writers_waiting += 1
            try:
                # Wait until no readers AND no other writers are active
                while self._num_readers > 0 or self._writer_active:
                    if self._num_readers > 0:
                        self._readers_ok.wait()
                    else:
                        self._writers_ok.wait()

            finally:
                self._writers_waiting -= 1

            self._writer_active = True

        try:
            yield
        finally:
            with self._lock:
                self._writer_active = False
                self._writers_ok.notify_all()
