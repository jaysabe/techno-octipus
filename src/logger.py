# logger.py – Action-sequence logger for ESP32 (MicroPython)
#
# Records every action taken inside the live loop and writes the full
# sequence to a file on the ESP32 flash when the session ends.
#
# Usage:
#   from logger import ActionLogger
#   log = ActionLogger()
#   log.record("move_base", angle=90)
#   log.save()           # writes to flash
#   log.dump()           # prints to REPL

import utime


class ActionLogger:
    """Collects action entries during a live loop and persists them to flash."""

    LOG_FILE = "/action_log.txt"

    def __init__(self):
        self._session_start = utime.ticks_ms()
        self._entries = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def record(self, action: str, **params):
        """Append one action to the in-memory sequence.

        Args:
            action: Human-readable action name, e.g. ``"move_base"``.
            **params: Optional key-value metadata (angle, speed, …).
        """
        elapsed_ms = utime.ticks_diff(utime.ticks_ms(), self._session_start)
        entry = {"t": elapsed_ms, "action": action, "params": params}
        self._entries.append(entry)

    def dump(self):
        """Print the recorded sequence to the MicroPython REPL."""
        print("=== Action Log ({} entries) ===".format(len(self._entries)))
        for i, e in enumerate(self._entries):
            print(
                "[{:>4}] +{:>6} ms  {}  {}".format(
                    i, e["t"], e["action"], e["params"]
                )
            )
        print("================================")

    def save(self):
        """Append the current session's log to :attr:`LOG_FILE` on flash."""
        if not self._entries:
            print("[logger] nothing to save.")
            return

        session_ts = utime.localtime()
        header = "# session {} entries  start={}\n".format(
            len(self._entries), _fmt_time(session_ts)
        )

        try:
            with open(self.LOG_FILE, "a") as fh:
                fh.write(header)
                for e in self._entries:
                    line = "{},{},{}\n".format(
                        e["t"], e["action"], _params_str(e["params"])
                    )
                    fh.write(line)
                fh.write("\n")
            print("[logger] saved {} entries to {}".format(
                len(self._entries), self.LOG_FILE
            ))
        except OSError as exc:
            print("[logger] ERROR writing log: {}".format(exc))

    def clear(self):
        """Reset the in-memory log (does not touch the file)."""
        self._entries = []
        self._session_start = utime.ticks_ms()

    @property
    def entries(self):
        """Read-only view of logged entries."""
        return list(self._entries)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _fmt_time(t):
    """Format a ``utime.localtime()`` tuple as ``YYYY-MM-DD HH:MM:SS``."""
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        t[0], t[1], t[2], t[3], t[4], t[5]
    )


def _params_str(params: dict) -> str:
    """Serialize a params dict to a compact ``key=value`` string."""
    if not params:
        return ""
    return " ".join("{}={}".format(k, v) for k, v in params.items())
