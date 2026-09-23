from policyengine_us.model_api import *


class total_unemployment_compensation(Variable):
    value_type = float
    entity = Person
    label = "total unemployment compensation"
    unit = USD
    documentation = (
        "Unemployment compensation used in downstream income flows, using "
        "the reported (uprated) amount when present and otherwise falling "
        "back to the modeled state unemployment insurance programs. A "
        "reported amount above 0 overrides modeled unemployment insurance; a "
        "reported 0 is treated as not reported. To suppress modeled "
        "unemployment insurance, leave the state unemployment insurance wage "
        "and weeks inputs at 0."
    )
    definition_period = YEAR

    def formula(person, period, parameters):
        reported = person("unemployment_compensation", period)
        modeled = person("modeled_state_unemployment_compensation", period)
        return where(reported > 0, reported, modeled)
