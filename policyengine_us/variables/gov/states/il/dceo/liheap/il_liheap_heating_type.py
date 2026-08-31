from policyengine_us.model_api import *


class ILLIHEAPHeatingType(Enum):
    ALL_ELECTRIC = "All Electric"
    NAT_GAS_OTHER = "Natural Gas / Other"
    PROPANE_FUEL_OIL = "Propane / Fuel Oil"
    CASH = "Cash (heat included in rent)"


class il_liheap_heating_type(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = ILLIHEAPHeatingType
    default_value = ILLIHEAPHeatingType.ALL_ELECTRIC
    definition_period = YEAR
    label = "Household heating type for IL LIHEAP"
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        heating_type = spm_unit("heating_type", period)
        types = heating_type.possible_values
        deliverable_fuel = (
            (heating_type == types.PROPANE)
            | (heating_type == types.FUEL_OIL)
            | (heating_type == types.KEROSENE)
        )
        return select(
            [
                heat_in_rent,
                (heating_type == types.ELECTRICITY) | (heating_type == types.SOLAR),
                deliverable_fuel,
            ],
            [
                ILLIHEAPHeatingType.CASH,
                ILLIHEAPHeatingType.ALL_ELECTRIC,
                ILLIHEAPHeatingType.PROPANE_FUEL_OIL,
            ],
            default=ILLIHEAPHeatingType.NAT_GAS_OTHER,
        )
