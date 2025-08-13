"""
labx package public API.

This exposes the main LabxClient methods from a single shared instance,
so users can simply call:

    import labx
    labx.connect()
    labx.connected()
    labx.profiles()
    labx.tasks()
    labx.run(...)

without needing to manage LabxClient directly.
"""

from .client import LabxClient, DEFAULT_LABX_URL

# Singleton instance
_client = LabxClient()

# Methods
# Public API methods bound to the singleton
for name in ("connect", "profiles", "tasks", "run"):
    globals()[name] = getattr(_client, name)

# State
def connected():
    return _client.connected

# What gets imported with `from labx import *`
__all__ = [
    "DEFAULT_LABX_URL",
    "connect",
    "profiles",
    "tasks",
    "run",
]
