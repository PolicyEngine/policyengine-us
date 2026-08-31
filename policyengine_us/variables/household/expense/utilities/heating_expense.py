from policyengine_us.model_api import *


class heating_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "Heating expense"
    unit = USD
    definition_period = YEAR
    documentation = "Annual home heating expense: the fuel bill matching the household's primary heating type (mixed-fuel households are represented by their primary fuel's bill). Programs that cap benefits at actual heating costs read this variable rather than arbitrating between expense inputs."

    def formula(spm_unit, period, parameters):
        heating_type = spm_unit("heating_type", period)
        types = heating_type.possible_values
        fuel_bill = select(
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
            # NONE has no fuel bill.
            default=0,
        )
        # Deprecated fallbacks under the atomic-inputs migration:
        # heating_expense_person and heating_cooling_expense predate the
        # per-fuel vocabulary and are still sent by some API users.
        person_level = add(spm_unit, period, ["heating_expense_person"])
        heating_cooling = spm_unit("heating_cooling_expense", period)
        return select(
            [fuel_bill > 0, person_level > 0],
            [fuel_bill, person_level],
            default=heating_cooling,
        )
