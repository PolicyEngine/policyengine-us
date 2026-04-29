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
        return where(
            heat_in_rent,
            ILLIHEAPHeatingType.CASH,
            ILLIHEAPHeatingType.ALL_ELECTRIC,
        )
