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
    documentation = "Derived from heat_expense_included_in_rent and the canonical heating_type input: heat in rent is the cash category; electricity and solar are all-electric; propane, fuel oil and kerosene share the propane / fuel oil row; natural gas, wood, coal, other fuels and no heating share the natural gas / other row. UNSPECIFIED keeps the pre-canonical default of all-electric. Setting this directly is deprecated during the vocabulary migration and changes only the matrix row: the expense cap still follows the canonical heating_type."
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        heating_type = spm_unit("heating_type", period)
        types = heating_type.possible_values
        # UNSPECIFIED keeps the pre-canonical default of all-electric.
        all_electric = (
            (heating_type == types.ELECTRICITY)
            | (heating_type == types.SOLAR)
            | (heating_type == types.UNSPECIFIED)
        )
        deliverable_fuel = (
            (heating_type == types.PROPANE)
            | (heating_type == types.FUEL_OIL)
            | (heating_type == types.KEROSENE)
        )
        # The matrix labels this row "Nat. Gas / Other".
        gas_or_other = (
            (heating_type == types.NATURAL_GAS)
            | (heating_type == types.WOOD)
            | (heating_type == types.COAL)
            | (heating_type == types.OTHER)
            | (heating_type == types.NONE)
        )
        return select(
            [
                heat_in_rent,
                all_electric,
                deliverable_fuel,
                gas_or_other,
            ],
            [
                ILLIHEAPHeatingType.CASH,
                ILLIHEAPHeatingType.ALL_ELECTRIC,
                ILLIHEAPHeatingType.PROPANE_FUEL_OIL,
                ILLIHEAPHeatingType.NAT_GAS_OTHER,
            ],
            default=ILLIHEAPHeatingType.ALL_ELECTRIC,
        )
