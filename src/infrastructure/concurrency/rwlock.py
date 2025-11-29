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
        self._lock = threading.Lock()  # Protects internal state
        self._readers_ok = threading.Condition(self._lock)
        self._writers_ok = threading.Condition(self._lock)

        self._num_readers = 0  # Active readers
        self._writer_active = False  # Is a writer currently writing?

    @contextmanager
    def read_lock(self):
        """Context manager for acquiring a shared read lock."""
        with self._lock:
            # Wait until no writer is active
            while self._writer_active:
                self._writers_ok.wait()
            self._num_readers += 1

        try:
            yield  # Critical section (reading happens here)
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
            # Wait until no readers AND no other writers are active
            while self._num_readers > 0 or self._writer_active:
                # Use wait() which releases the lock and blocks until notified
                if self._num_readers > 0:
                    self._readers_ok.wait()
                else:
                    self._writers_ok.wait()

            self._writer_active = True

        try:
            yield  # Critical section (writing happens here)
        finally:
            with self._lock:
                self._writer_active = False
                # Notify everyone. Writers get first dibs usually, but notify_all is safer
                self._writers_ok.notify_all()
                self._readers_ok.notify_all()
