"""
Snowflake ID Generator — From-Scratch Implementation (R11)

Based on Twitter's Snowflake algorithm as described in
"System Design Interview" by Alex Xu (Chapter 7).

Layout of a 64-bit Snowflake ID:
┌──────────────────────────────────────────────────────────────────┐
│ 0 │        41-bit timestamp         │ 10-bit machine │ 12-bit seq │
└──────────────────────────────────────────────────────────────────┘

- Bit 0: sign bit (always 0)
- Bits 1–41: milliseconds since custom epoch (2024-01-01)
- Bits 42–51: machine/worker ID (supports 1024 machines)
- Bits 52–63: per-machine sequence number (4096 IDs per ms)

Trade-offs:
  - Time-sortable: IDs are roughly chronological
  - Decentralised: no coordination needed between machines
  - Compact: fits in a 64-bit integer (vs 128-bit UUID)
  - Limitation: clock rollback can cause duplicates (mitigated by waiting)
"""

import time
import threading


# Custom epoch: 2024-01-01T00:00:00Z in milliseconds
EPOCH = 1704067200000

MACHINE_ID_BITS = 10
SEQUENCE_BITS = 12

MAX_MACHINE_ID = (1 << MACHINE_ID_BITS) - 1  # 1023
MAX_SEQUENCE = (1 << SEQUENCE_BITS) - 1       # 4095

MACHINE_ID_SHIFT = SEQUENCE_BITS              # 12
TIMESTAMP_SHIFT = MACHINE_ID_BITS + SEQUENCE_BITS  # 22


class SnowflakeIDGenerator:
    """Thread-safe Snowflake ID generator.

    Each instance is bound to a machine_id and maintains its own
    sequence counter.  Generates up to 4096 unique IDs per millisecond
    per machine.
    """

    def __init__(self, machine_id: int):
        if machine_id < 0 or machine_id > MAX_MACHINE_ID:
            raise ValueError(f"machine_id must be between 0 and {MAX_MACHINE_ID}")

        self.machine_id = machine_id
        self.sequence = 0
        self.last_timestamp = -1
        self._lock = threading.Lock()

    def _current_millis(self) -> int:
        return int(time.time() * 1000)

    def _wait_next_millis(self, last_ts: int) -> int:
        ts = self._current_millis()
        while ts <= last_ts:
            ts = self._current_millis()
        return ts

    def generate(self) -> int:
        """Generate a new unique Snowflake ID.

        Thread-safe: uses a lock to protect the sequence counter.
        If the sequence overflows within the same millisecond,
        the generator waits until the next millisecond.
        """
        with self._lock:
            ts = self._current_millis()

            # Clock moved backward — defensive wait
            if ts < self.last_timestamp:
                ts = self._wait_next_millis(self.last_timestamp)

            if ts == self.last_timestamp:
                # Same millisecond: increment sequence
                self.sequence = (self.sequence + 1) & MAX_SEQUENCE
                if self.sequence == 0:
                    # Sequence overflow — wait until next ms
                    ts = self._wait_next_millis(ts)
            else:
                self.sequence = 0

            self.last_timestamp = ts

            snowflake_id = (
                ((ts - EPOCH) << TIMESTAMP_SHIFT)
                | (self.machine_id << MACHINE_ID_SHIFT)
                | self.sequence
            )

            return snowflake_id

    @staticmethod
    def extract_timestamp(snowflake_id: int) -> int:
        """Extract the Unix timestamp (ms) from a Snowflake ID."""
        return ((snowflake_id >> TIMESTAMP_SHIFT) + EPOCH)

    @staticmethod
    def extract_machine_id(snowflake_id: int) -> int:
        """Extract the machine ID from a Snowflake ID."""
        return (snowflake_id >> MACHINE_ID_SHIFT) & MAX_MACHINE_ID

    @staticmethod
    def extract_sequence(snowflake_id: int) -> int:
        """Extract the sequence number from a Snowflake ID."""
        return snowflake_id & MAX_SEQUENCE


# Module-level singleton — initialised by the app at startup
_generator: SnowflakeIDGenerator | None = None


def init_generator(machine_id: int):
    """Initialise the module-level Snowflake generator."""
    global _generator
    _generator = SnowflakeIDGenerator(machine_id)


def generate_id() -> int:
    """Generate a Snowflake ID using the module-level generator."""
    if _generator is None:
        raise RuntimeError("SnowflakeIDGenerator not initialised — call init_generator() first")
    return _generator.generate()
