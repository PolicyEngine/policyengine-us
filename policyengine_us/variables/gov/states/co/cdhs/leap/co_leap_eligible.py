from policyengine_us.model_api import *


class co_leap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for Colorado LEAP regular heating assistance"
    defined_for = StateCode.CO
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/CO_Plan_2026.pdf#page=5,8",
        "https://drive.google.com/file/d/1G3XKsXyKoPZmsA5-P6NI6w3svP99xOZd/view#page=46,51,52,53,55",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("co_leap_household_size", period)
        income = spm_unit("co_leap_countable_income", period)
        limit = spm_unit("co_leap_income_limit", period)
        cost = spm_unit("co_leap_heating_cost", period)
        included = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit("receives_housing_assistance", period)
        fuel = spm_unit("heating_type", period)
        fuels = fuel.possible_values
        # Subsidized rent-included heat can qualify with a separate surcharge;
        # that fact is unavailable, so this exception is not represented.
        # Application timing, vendor approval and prior receipt are not modeled.
        return (
            (size > 0)
            & (income <= limit)
            & (cost > 0)
            & (fuel != fuels.NONE)
            & (fuel != fuels.UNSPECIFIED)
            & ~(included & subsidized)
        )
