from policyengine_us.model_api import *
from policyengine_core.simulations import Simulation
from policyengine_us.variables.household.demographic.geographic.ucgid.ucgid_enum import (
    UCGID,
)
import numpy as np


class ucgid(Variable):
    value_type = Enum
    possible_values = UCGID
    default_value = UCGID.US
    entity = Household
    label = "Unified Congressional Geographic Identifier (UCGID)"
    definition_period = YEAR
    documentation = """
    Unified Congressional Geographic Identifier (UCGID) for the household as defined by the U.S. Census Bureau.
    """

    def formula(household, period, parameters):
        simulation: Simulation = household.simulation

        # Check if this variable has been set as input
        if simulation.get_holder("ucgid").get_known_periods():
            return household("ucgid", period)

        # Try to derive from state_code
        state_code_enum = household("state_code", period)
        state_code_strings = state_code_enum.decode_to_str()

        # Map state codes to UCGID state values
        state_mapping = {
            "AL": UCGID.AL,
            "AK": UCGID.AK,
            "AZ": UCGID.AZ,
            "AR": UCGID.AR,
            "CA": UCGID.CA,
            "CO": UCGID.CO,
            "CT": UCGID.CT,
            "DE": UCGID.DE,
            "DC": UCGID.DC,
            "FL": UCGID.FL,
            "GA": UCGID.GA,
            "HI": UCGID.HI,
            "ID": UCGID.ID,
            "IL": UCGID.IL,
            "IN": UCGID.IN,
            "IA": UCGID.IA,
            "KS": UCGID.KS,
            "KY": UCGID.KY,
            "LA": UCGID.LA,
            "ME": UCGID.ME,
            "MD": UCGID.MD,
            "MA": UCGID.MA,
            "MI": UCGID.MI,
            "MN": UCGID.MN,
            "MS": UCGID.MS,
            "MO": UCGID.MO,
            "MT": UCGID.MT,
            "NE": UCGID.NE,
            "NV": UCGID.NV,
            "NH": UCGID.NH,
            "NJ": UCGID.NJ,
            "NM": UCGID.NM,
            "NY": UCGID.NY,
            "NC": UCGID.NC,
            "ND": UCGID.ND,
            "OH": UCGID.OH,
            "OK": UCGID.OK,
            "OR": UCGID.OR,
            "PA": UCGID.PA,
            "RI": UCGID.RI,
            "SC": UCGID.SC,
            "SD": UCGID.SD,
            "TN": UCGID.TN,
            "TX": UCGID.TX,
            "UT": UCGID.UT,
            "VT": UCGID.VT,
            "VA": UCGID.VA,
            "WA": UCGID.WA,
            "WV": UCGID.WV,
            "WI": UCGID.WI,
            "WY": UCGID.WY,
        }

        # Convert state code strings to UCGID values
        result = np.empty(len(state_code_strings), dtype=object)
        for i, state_str in enumerate(state_code_strings):
            if state_str in state_mapping:
                result[i] = state_mapping[state_str]
            else:
                result[i] = UCGID.US

        return result
