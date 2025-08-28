from policyengine_us.model_api import *


class az_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Arizona LIHEAP eligible"
    definition_period = YEAR
    defined_for = StateCode.AZ
    reference = (
        "https://des.az.gov/services/basic-needs/liheap",
        "45 CFR Part 96 Subpart H",
    )

    def formula(spm_unit, period, parameters):
        # Income eligible or categorically eligible
        income_eligible = spm_unit("az_liheap_income_eligible", period)
        categorical_eligible = spm_unit(
            "az_liheap_categorical_eligible", period
        )

        # Must be responsible for energy costs
        has_energy_costs = (
            add(
                spm_unit,
                period,
                [
                    "heating_cooling_expense",
                    "electricity_expense",
                    "gas_expense",
                ],
            )
            > 0
        )

        return (income_eligible | categorical_eligible) & has_energy_costs
