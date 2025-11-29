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


def test_writer_priority_over_new_readers():
    """
    Verify that a WAITING writer blocks new readers (Anti-Starvation).

    Scenario:
    1. Reader 1 holds the lock.
    2. Writer attempts to acquire lock and blocks (increments _writers_waiting).
    3. Reader 2 attempts to acquire lock.

    Expected: Reader 2 must NOT acquire the lock until after the Writer has finished.
    """
    lock = RWLock()
    log = []

    # Synchronization events
    r1_acquired = threading.Event()
    writer_queued = threading.Event()

    def reader_1_task():
        with lock.read_lock():
            r1_acquired.set()
            time.sleep(0.2)  # Hold lock to force writer to wait
            log.append("R1_done")

    def writer_task():
        r1_acquired.wait()  # Ensure R1 has the lock
        writer_queued.set()  # Signal that we are about to request lock

        # This should block until R1 releases
        # Crucially, simply entering this context manager increments _writers_waiting
        with lock.write_lock():
            log.append("Writer_work")

    def reader_2_task():
        writer_queued.wait()
        # Give the writer a tiny moment to execute the 'waiting' increment logic
        time.sleep(0.05)

        # If priority logic is working, this blocks.
        # If broken, R2 enters immediately because R1 is still holding read lock.
        with lock.read_lock():
            log.append("R2_work")

    t_r1 = threading.Thread(target=reader_1_task)
    t_w = threading.Thread(target=writer_task)
    t_r2 = threading.Thread(target=reader_2_task)

    t_r1.start()
    t_w.start()
    t_r2.start()

    t_r1.join()
    t_w.join()
    t_r2.join()

    # If R2 ran before Writer, starvation protection failed.
    # Correct order: R1 finishes -> Writer runs -> R2 runs
    assert log == ["R1_done", "Writer_work", "R2_work"]


def test_internal_state_integrity():
    """
    White-box testing to ensure internal counters are reset correctly
    even after heavy contention.
    """
    lock = RWLock()

    def mixed_work():
        with lock.read_lock():
            time.sleep(0.001)
        with lock.write_lock():
            time.sleep(0.001)

    threads = [threading.Thread(target=mixed_work) for _ in range(20)]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    # Verify internal state is clean
    assert lock._num_readers == 0
    assert lock._writer_active is False
    assert lock._writers_waiting == 0
