from policyengine_us.model_api import *


class has_gas_and_fuel_expense(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Has gas or fuel costs"
    documentation = "Whether the household pays any gas or fuel bill: metered natural gas, propane, fuel oil, kerosene, wood, coal, other heating fuel, or cooking fuel. SNAP publishes one individual standard for gas and fuel together, so these bills count as a single utility."
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-7/section-273.9#p-273.9(d)(6)(iii)(A)(1)"
    )

    def formula(spm_unit, period, parameters):
        return (
            add(
                spm_unit,
                period,
                [
                    "gas_expense",
                    "bottled_gas_expense",
                    "fuel_oil_expense",
                    "wood_expense",
                    "coal_expense",
                    "other_heating_fuel_expense",
                    "cooking_fuel_expense",
                ],
            )
            > 0
        )
