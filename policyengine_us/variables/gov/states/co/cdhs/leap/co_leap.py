from policyengine_us.model_api import *


class co_leap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Colorado LEAP regular heating assistance"
    defined_for = "co_leap_eligible"
    # PDF pages 92-95
    reference = (
        "https://drive.google.com/file/d/1G3XKsXyKoPZmsA5-P6NI6w3svP99xOZd/view#page=92"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.co.cdhs.leap.payment
        heating_cost = spm_unit("co_leap_heating_cost", period)
        contribution = spm_unit("co_leap_income_contribution_rate", period)
        # Every SPM unit at the address counts, including ineligible units.
        # This approximates economic units sharing a meter; actual separate
        # meters and the administrative nine-household limit are not observed.
        shared_households = add(spm_unit.household, period, ["spm_unit_count"])
        shared_cost = (
            heating_cost
            * (1 - p.initial_reduction)
            * (1 - contribution)
            / max_(shared_households, 1)
        )
        subsidized = spm_unit("receives_housing_assistance", period)
        adjusted = shared_cost - subsidized * p.subsidized_housing_deduction
        # FY2026 verified policy; parameter backfilling does not verify prior
        # years. The minimum applies even when adjusted costs are smaller.
        return clip(adjusted, p.minimum, p.maximum)
