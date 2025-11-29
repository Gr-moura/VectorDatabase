# tests/test_infrastructure/test_rwlock.py

import threading
import time
from src.infrastructure.concurrency.rwlock import RWLock


def test_single_thread_read_write():
    """Basic sanity check: does it work in a single thread?"""
    lock = RWLock()

    with lock.read_lock():
        assert lock._num_readers == 1
        assert not lock._writer_active

    assert lock._num_readers == 0

    with lock.write_lock():
        assert lock._writer_active
        assert lock._num_readers == 0

    assert not lock._writer_active


def test_multiple_readers_concurrently():
    """Verify that multiple readers can hold the lock simultaneously."""
    lock = RWLock()
    reader_count = 0

    def reader_task():
        nonlocal reader_count
        with lock.read_lock():
            reader_count += 1
            time.sleep(0.1)  # Simulate work

    threads = [threading.Thread(target=reader_task) for _ in range(5)]

    for t in threads:
        t.start()

    # Give threads a moment to start and acquire lock
    time.sleep(0.05)

    # Crucial assertion: All 5 threads should be inside the critical section
    # at the same time because readers don't block readers.
    # Note: This relies on timing, so it's slightly brittle, but standard for lock testing.
    with lock._lock:  # Peek at internal state safely
        active_readers = lock._num_readers

    assert (
        active_readers > 1
    )  # Should be 5 ideally, but definitely > 1 implies concurrency

    for t in threads:
        t.join()


def test_writer_blocks_readers():
    """Verify that a writer blocks new readers from entering."""
    lock = RWLock()
    log = []

    def writer_task():
        with lock.write_lock():
            log.append("writer_start")
            time.sleep(0.2)
            log.append("writer_end")

    def reader_task():
        # Delay slightly to ensure writer gets there first
        time.sleep(0.05)
        with lock.read_lock():
            log.append("reader_run")

    t_writer = threading.Thread(target=writer_task)
    t_reader = threading.Thread(target=reader_task)

    t_writer.start()
    t_reader.start()

    t_writer.join()
    t_reader.join()

    # Expected order: Writer starts -> Writer ends -> Reader runs
    # If Reader ran during Writer, we'd see "reader_run" between start/end
    assert log == ["writer_start", "writer_end", "reader_run"]


def test_readers_block_writer():
    """Verify that a writer waits for existing readers to finish."""
    lock = RWLock()
    log = []

    def reader_task():
        with lock.read_lock():
            log.append("reader_start")
            time.sleep(0.2)
            log.append("reader_end")

    def writer_task():
        time.sleep(0.05)  # Ensure reader starts first
        with lock.write_lock():
            log.append("writer_run")

    t_reader = threading.Thread(target=reader_task)
    t_writer = threading.Thread(target=writer_task)

    t_reader.start()
    t_writer.start()

    t_reader.join()
    t_writer.join()

    # Writer must wait for reader to finish
    assert log == ["reader_start", "reader_end", "writer_run"]


def test_writer_blocks_writer():
    """Verify that writers are mutually exclusive."""
    lock = RWLock()
    shared_resource = 0

    def writer_task():
        nonlocal shared_resource
        with lock.write_lock():
            # Read-modify-write operation that is unsafe without locks
            temp = shared_resource
            time.sleep(0.01)  # Force context switch opportunity
            shared_resource = temp + 1

    threads = [threading.Thread(target=writer_task) for _ in range(10)]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    # If locks work, result is 10. If race condition, result < 10.
    assert shared_resource == 10
