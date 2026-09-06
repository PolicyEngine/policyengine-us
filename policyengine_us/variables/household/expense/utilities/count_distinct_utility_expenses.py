from policyengine_us.model_api import *


class count_distinct_utility_expenses(Variable):
    value_type = int
    entity = SPMUnit
    label = "Number of distinct utility expenses"
    documentation = "The number of distinct utility expenses the household pays, counted by the SNAP individual-standard categories: electricity, gas and fuel (one category for metered gas and every deliverable or cooking fuel), telephone, trash, water, and sewage. The deprecated heating_cooling_expense input still counts as its own category for unmigrated households."
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-7/section-273.9#p-273.9(d)(6)(iii)(A)"
    )

    def formula(spm_unit, period, parameters):
        has_expense = [
            spm_unit("heating_cooling_expense", period) > 0,
            # Use pre-subsidy expenses to avoid circular references
            # since electricity subsidies depend on SNAP enrollment.
            spm_unit("pre_subsidy_electricity_expense", period) > 0,
            spm_unit("has_gas_and_fuel_expense", period),
            spm_unit("has_phone_expense", period),
            spm_unit("trash_expense", period) > 0,
            spm_unit("water_expense", period) > 0,
            spm_unit("sewage_expense", period) > 0,
        ]
        return sum(has_expense)
