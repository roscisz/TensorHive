class ProtectionHandler():
    _protection_behaviour = None

    def __init__(self, behaviour: _protection_behaviour):
        self._protection_behaviour = behaviour

    def trigger_action(self, *args, **kwargs) -> None:
        self._protection_behaviour.trigger_action(*args, **kwargs)
