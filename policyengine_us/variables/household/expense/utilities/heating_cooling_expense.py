from policyengine_us.model_api import *


class heating_cooling_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "Heating and cooling expense"
    unit = USD
    definition_period = YEAR
    documentation = "Deprecated for heating amounts: set heating_type and the matching per-fuel expense instead; this input remains only as a fallback inside the IL and MA LIHEAP adapters for households whose heating_type is UNSPECIFIED. Still read directly by the SNAP utility allowance determination pending its own migration."
