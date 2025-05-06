from policyengine_us.model_api import *


class MassachusettsLIHEAPUtilityCategory(Enum):
    DELIVERABLE_FUEL = "Deliverable Fuel"
    UTILITY_AND_HEAT_IN_RENT = "Utility and Heat in Rent" 


class ma_liheap_utility_category(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = MassachusettsLIHEAPUtilityCategory
    default_value = MassachusettsLIHEAPUtilityCategory.DELIVERABLE_FUEL
    definition_period = YEAR
    defined_for = StateCode.MA
    label = "Massachusetts LIHEAP Household Utility type"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ma.doer.liheap
        heating_type = spm_unit("ma_liheap_heating_type", period)
        deliverable_fuel = np.isin(heating_type, p.deliverable_fuel)
        utility_and_heat_in_rent = np.isin(
            heating_type, p.utility_and_heat_in_rent
        )

        conditions = [
            deliverable_fuel,
            utility_and_heat_in_rent,
        ]
        results = [
            MassachusettsLIHEAPUtilityCategory.DELIVERABLE_FUEL,
            MassachusettsLIHEAPUtilityCategory.UTILITY_AND_HEAT_IN_RENT,
        ]

        return select(
            conditions,
            results,
            default=MassachusettsLIHEAPUtilityCategory.DELIVERABLE_FUEL,
        )
