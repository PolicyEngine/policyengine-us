from policyengine_us.model_api import *


class utility_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "Utility expenses"
    unit = USD
    documentation = (
        "Total utility bills the household pays separately from rent: electricity, "
        "every gas and fuel bill, water, sewage, trash, and telephone. Households "
        "whose heating_type is UNSPECIFIED also add the deprecated "
        "heating_cooling_expense input, as before the canonical heating inputs "
        "existed; a known heating type reads only the per-fuel bills, so the heating "
        "cost is never counted twice."
    )
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        heating_type = spm_unit("heating_type", period)
        unspecified = heating_type == heating_type.possible_values.UNSPECIFIED
        bills = add(
            spm_unit,
            period,
            [
                "electricity_expense",
                "gas_expense",
                "bottled_gas_expense",
                "fuel_oil_expense",
                "wood_expense",
                "coal_expense",
                "other_heating_fuel_expense",
                "cooking_fuel_expense",
                "water_expense",
                "sewage_expense",
                "trash_expense",
                "phone_expense",
            ],
        )
        legacy_expense = spm_unit("heating_cooling_expense", period)
        return bills + where(unspecified, legacy_expense, 0)
