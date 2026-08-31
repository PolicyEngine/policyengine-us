from policyengine_us.model_api import *


class DCLIHEAPHeatingType(Enum):
    ELECTRICITY = "Electricity"
    GAS = "Gas"
    HEAT_IN_RENT = "Heat in Rent"  # Electricity or gas included in rent
    OIL = "Oil"


class dc_liheap_heating_type(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = DCLIHEAPHeatingType
    default_value = DCLIHEAPHeatingType.ELECTRICITY
    definition_period = YEAR
    label = "Household heating types for DC LIHEAP"
    documentation = "Derived from the canonical heating_type input; setting this directly is deprecated during the vocabulary migration."

    def formula(spm_unit, period, parameters):
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        heating_type = spm_unit("heating_type", period)
        types = heating_type.possible_values
        # DC's benefit matrix has one deliverable-fuel row (oil); other
        # deliverable fuels map to it, and fuels without a matrix row take
        # the electricity row.
        deliverable_fuel = (
            (heating_type == types.FUEL_OIL)
            | (heating_type == types.KEROSENE)
            | (heating_type == types.PROPANE)
        )
        return select(
            [
                heat_in_rent,
                heating_type == types.NATURAL_GAS,
                deliverable_fuel,
            ],
            [
                DCLIHEAPHeatingType.HEAT_IN_RENT,
                DCLIHEAPHeatingType.GAS,
                DCLIHEAPHeatingType.OIL,
            ],
            # UNSPECIFIED keeps the pre-canonical default of electricity.
            default=DCLIHEAPHeatingType.ELECTRICITY,
        )
