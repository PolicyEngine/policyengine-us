from policyengine_us.model_api import *


class heating_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "Heating expense"
    unit = USD
    definition_period = YEAR
    documentation = "Annual home heating expense: the fuel bill matching the household's primary heating type (mixed-fuel households are represented by their primary fuel's bill). Zero is a valid value. UNSPECIFIED and NONE heating types have no bill here; UNSPECIFIED households are handled by each program's deprecated legacy adapter instead."
    reference = "https://data.census.gov/table/ACSDT1Y2023.B25040"

    def formula(spm_unit, period, parameters):
        heating_type = spm_unit("heating_type", period)
        types = heating_type.possible_values
        return select(
            [
                # Solar-primary homes are assumed grid-tied with electric
                # supplemental heat; fully off-grid homes have no
                # electricity bill and get zero.
                (heating_type == types.ELECTRICITY) | (heating_type == types.SOLAR),
                heating_type == types.NATURAL_GAS,
                (heating_type == types.FUEL_OIL) | (heating_type == types.KEROSENE),
                heating_type == types.PROPANE,
                heating_type == types.WOOD,
                heating_type == types.COAL,
                heating_type == types.OTHER,
            ],
            [
                # Pre-subsidy electricity avoids circular references:
                # electricity_expense nets out subsidy programs that depend
                # on benefit enrollment.
                spm_unit("pre_subsidy_electricity_expense", period),
                spm_unit("gas_expense", period),
                spm_unit("fuel_oil_expense", period),
                spm_unit("bottled_gas_expense", period),
                spm_unit("wood_expense", period),
                spm_unit("coal_expense", period),
                spm_unit("other_heating_fuel_expense", period),
            ],
            # UNSPECIFIED and NONE: no canonical bill.
            default=0,
        )
