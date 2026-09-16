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
    documentation = "Derived from heat_expense_included_in_rent and the canonical heating_type input. Fuel oil, kerosene and propane take the oil row; wood, coal, other and solar heating have no DC matrix row and take the electricity row, as do UNSPECIFIED and NONE. Setting this directly is deprecated during the vocabulary migration and changes only the matrix row: the expense cap still follows the canonical heating_type."
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        heating_type = spm_unit("heating_type", period)
        types = heating_type.possible_values
        # DC's matrix has electricity, gas, oil and heat-in-rent rows only.
        # Kerosene and propane are priced on the oil row. Fuels without a
        # row take the electricity row: it is the lowest matrix amount and
        # the pre-canonical default, which UNSPECIFIED keeps.
        oil_row = (
            (heating_type == types.FUEL_OIL)
            | (heating_type == types.KEROSENE)
            | (heating_type == types.PROPANE)
        )
        electricity_row = (
            (heating_type == types.ELECTRICITY)
            | (heating_type == types.SOLAR)
            | (heating_type == types.WOOD)
            | (heating_type == types.COAL)
            | (heating_type == types.OTHER)
            | (heating_type == types.NONE)
            | (heating_type == types.UNSPECIFIED)
        )
        return select(
            [
                heat_in_rent,
                heating_type == types.NATURAL_GAS,
                oil_row,
                electricity_row,
            ],
            [
                DCLIHEAPHeatingType.HEAT_IN_RENT,
                DCLIHEAPHeatingType.GAS,
                DCLIHEAPHeatingType.OIL,
                DCLIHEAPHeatingType.ELECTRICITY,
            ],
            default=DCLIHEAPHeatingType.ELECTRICITY,
        )
