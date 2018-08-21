from abc import ABC, abstractmethod
from typing import Dict
from tensorhive.core.monitors.MonitoringBehaviour import MonitoringBehaviour


class Monitor():
    _monitoring_behaviour = None
    _gathered_data = {}

    def __init__(self, behaviour: MonitoringBehaviour):
        self._monitoring_behaviour = behaviour

    @property
    def gathered_data(self) -> Dict:
        return self._gathered_data

    def update(self, group_connection) -> None:
        self._gathered_data = self._monitoring_behaviour.update(
            group_connection)
