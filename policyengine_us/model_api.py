from policyengine_us.variables.household.demographic.geographic.state_code import (
    StateCode,
)
from functools import reduce
from policyengine_core.model_api import *
from policyengine_us.entities import *
from policyengine_us.tools.general import *
from pathlib import Path
from policyengine_us.typing import *
import warnings
from policyengine_us.tools.cloning import get_stored_variables
import numpy as np

warnings.filterwarnings("ignore")

REPO = Path(__file__).parent


def all_of_variables(variables: List[str]) -> Formula:
    def formula(entity, period, parameters):
        value = True
        for variable in variables:
            value = value & (add(entity, period, [variable]) > 0)
        return value

    return formula


STATES = [
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DC",
    "DE",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
]


def random(population):
    """
    Generate random values for each entity in the population.

    Args:
        population: The population object containing simulation data.

    Returns:
        np.ndarray: Array of random values for each entity.
    """
    # Initialize count of random calls if not already present
    if not hasattr(population.simulation, "count_random_calls"):
        population.simulation.count_random_calls = 0
    population.simulation.count_random_calls += 1

    # Get known periods or use default calculation period
    known_periods = population.simulation.get_holder(
        f"{population.entity.key}_id"
    ).get_known_periods()
    period = (
        known_periods[0]
        if known_periods
        else population.simulation.default_calculation_period
    )

    # Get entity IDs for the period
    entity_ids = population(f"{population.entity.key}_id", period)

    # Generate random values for each entity
    values = np.array(
        [
            np.random.default_rng(
                seed=id * 100 + population.simulation.count_random_calls
            ).random()
            for id in entity_ids
        ]
    )

    return values
