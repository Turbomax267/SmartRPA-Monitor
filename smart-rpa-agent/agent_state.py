import json
from copy import deepcopy

from config import AGENT_STATE_PATH

DEFAULT_STATE = {
    "enabled_rpas": {},
}


class AgentState:
    def __init__(self):
        self.path = AGENT_STATE_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.save(deepcopy(DEFAULT_STATE))

    def load(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, state):
        self.path.write_text(json.dumps(state, indent=2, ensure_ascii=True), encoding="utf-8")

    def is_enabled(self, rpa_code):
        return bool(self.load().get("enabled_rpas", {}).get(rpa_code, False))

    def set_enabled(self, rpa_code, enabled):
        state = self.load()
        state.setdefault("enabled_rpas", {})[rpa_code] = bool(enabled)
        self.save(state)
