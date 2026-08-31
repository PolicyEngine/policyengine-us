from policyengine_us.model_api import *


class heating_cooling_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "Heating and cooling expense"
    unit = USD
    definition_period = YEAR
    documentation = "Deprecated for heating amounts: set heating_type and the matching per-fuel expense instead; heating_expense reads those and falls back to this input. Still read directly by the SNAP utility allowance determination pending its own migration."
