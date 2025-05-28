from policyengine_us.model_api import *


class MassachusettsLIHEAPUtilityCategory(Enum):
    UTILITY_AND_HEAT_IN_RENT = (
        "Utility and Heat in Rent"  # Electric, Natural Gas, Heat in Rent
    )
    DELIVERABLE_FUEL = (
        "Deliverable Fuel"  # Kerosene, Heating Oil, Propane, Other
    )
    NONE = "None"


class ma_liheap_utility_category(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = MassachusettsLIHEAPUtilityCategory
    default_value = MassachusettsLIHEAPUtilityCategory.NONE
    label = "Massachusetts LIHEAP household's utility category"
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = "https://www.mass.gov/doc/fy-2025-heap-income-eligibility-benefit-chart-may-8-2025/download"

    def formula(spm_unit, period, parameters):
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        heating_type = spm_unit("ma_liheap_heating_type", period)
        heating_types = heating_type.possible_values

        electricity = heating_type == heating_types.ELECTRICITY
        natural_gas = heating_type == heating_types.NATURAL_GAS
        heating_and_oil_propane = (
            heating_type == heating_types.HEATING_OIL_AND_PROPANE
        )
        kerosene = heating_type == heating_types.KEROSENE
        other = heating_type == heating_types.OTHER

        gas_or_electric_heating = electricity | natural_gas
        utility_and_heat_in_rent = gas_or_electric_heating | heat_in_rent

        deliverable_fuel = heating_and_oil_propane | kerosene | other

        conditions = [
            utility_and_heat_in_rent,
            deliverable_fuel,
        ]
        results = [
            MassachusettsLIHEAPUtilityCategory.UTILITY_AND_HEAT_IN_RENT,
            MassachusettsLIHEAPUtilityCategory.DELIVERABLE_FUEL,
        ]

        return select(
            conditions,
            results,
            default=MassachusettsLIHEAPUtilityCategory.NONE,
        )
