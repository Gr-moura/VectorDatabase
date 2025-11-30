# tests/test_infrastructure/test_rwlock.py

import threading
import time
import pytest
from src.infrastructure.concurrency.rwlock import RWLock

# ============================================================================
# Helpers for Robustness Testing
# ============================================================================


class SabotagedWaitError(Exception):
    """Custom exception to simulate a crash inside wait()."""

    pass


class SabotagedCondition:
    """
    A Proxy for threading.Condition that raises an exception
    when wait() is called, simulating a thread crash during lock acquisition.
    """

    def __init__(self, real_condition):
        self._real = real_condition

    def wait(self):
        # Simulate a crash exactly when the writer is blocked
        raise SabotagedWaitError("Writer crashed while waiting!")

    def notify_all(self):
        self._real.notify_all()

    def __getattr__(self, name):
        # Delegate other methods (acquire, release, etc.) to the real condition
        return getattr(self._real, name)


# ============================================================================
# Tests
# ============================================================================


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

        with lock.write_lock():
            log.append("Writer_work")

    def reader_2_task():
        writer_queued.wait()
        # Give the writer a tiny moment to execute the 'waiting' increment logic
        time.sleep(0.05)

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


def test_writer_crash_unblocks_waiting_readers():
    """
    Verify liveness: If a writer crashes while waiting for the lock,
    it must release its 'waiting' reservation so readers can proceed.

    Scenario:
    1. Reader 1 holds lock.
    2. Writer 1 waits (writers_waiting = 1).
       NOTE: Since Reader 1 is active, Writer 1 waits on _readers_ok condition!
    3. Reader 2 waits (blocked by writers_waiting > 0).
    4. Writer 1 crashes (simulated exception in wait()).
    5. Writer 1 must decrement writers_waiting and NOTIFY all.
    6. Reader 2 must wake up and acquire lock.
    """
    lock = RWLock()
    execution_log = []

    r1_acquired = threading.Event()
    w1_ready_to_crash = threading.Event()

    def r1_task():
        with lock.read_lock():
            r1_acquired.set()
            # Hold lock long enough for W1 to enter and R2 to enter
            time.sleep(0.5)
            execution_log.append("R1_RELEASED")

    def w1_task():
        r1_acquired.wait()
        # Sabotage BOTH conditions because we don't know for sure which one
        # the implementation will choose (though we know it's readers_ok here).
        original_readers_ok = lock._readers_ok
        original_writers_ok = lock._writers_ok

        lock._readers_ok = SabotagedCondition(original_readers_ok)
        lock._writers_ok = SabotagedCondition(original_writers_ok)

        try:
            w1_ready_to_crash.set()
            with lock.write_lock():
                execution_log.append("W1_ACQUIRED_IMPOSSIBLE")
        except SabotagedWaitError:
            execution_log.append("W1_CRASHED")
        finally:
            # Restore real conditions
            lock._readers_ok = original_readers_ok
            lock._writers_ok = original_writers_ok

    def r2_task():
        w1_ready_to_crash.wait()
        time.sleep(0.1)  # Ensure W1 is inside the wait block

        # R2 tries to acquire. If bug exists, R2 sleeps forever here.
        with lock.read_lock():
            execution_log.append("R2_ACQUIRED")

    t_r1 = threading.Thread(target=r1_task)
    t_w1 = threading.Thread(target=w1_task)
    t_r2 = threading.Thread(target=r2_task)

    t_r1.start()
    t_w1.start()
    t_r2.start()

    # Join with timeout to detect deadlock
    t_r1.join(timeout=2)
    t_w1.join(timeout=2)
    t_r2.join(timeout=2)

    if t_r2.is_alive():
        pytest.fail("DEADLOCK: Reader 2 never acquired lock after Writer crash.")

    assert "W1_CRASHED" in execution_log
    assert "R2_ACQUIRED" in execution_log

    # Verify state cleanup
    assert lock._writers_waiting == 0
    assert lock._num_readers == 0
    assert not lock._writer_active
