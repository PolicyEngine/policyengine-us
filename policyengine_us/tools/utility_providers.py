"""Build the model enums from the same ordered choices that partners display."""

import json
from importlib.resources import files

from policyengine_core.enums import Enum

_catalog = json.loads(
    files("policyengine_us")
    .joinpath("data", "utility_providers.json")
    .read_text(encoding="utf-8")
)


def _labels(variable: str) -> dict[str, str]:
    return {choice["value"]: choice["label"] for choice in _catalog[variable]}


ElectricityProvider = Enum("ElectricityProvider", _labels("electricity_provider"))
NaturalGasProvider = Enum("NaturalGasProvider", _labels("natural_gas_provider"))
