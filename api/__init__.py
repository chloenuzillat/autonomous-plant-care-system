"""HTTP REST API over the plant/sensor store, for consumers outside Python.

Python-side code calls `data.environmental_sensors.store` directly. The Unity
project in simulation/unity cannot, so this package puts the same data behind
HTTP. It is data-only: it serves species care ranges and logged readings, and
accepts readings back. It does not control the robot and owns no floor plan --
Unity does. See docs/unityApi.md.
"""
