from policyengine_us.model_api import *


class has_heating_cooling_expense(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Has heating/cooling costs"
    documentation = "Whether the household incurs heating or cooling costs separately from its rent or mortgage, which qualifies it for the SNAP heating and cooling standard utility allowance. Heating is the has_heating_expense fact and cooling is the has_cooling_expense fact. Households whose heating_type is UNSPECIFIED keep the pre-canonical signal, a positive heating_cooling_expense."
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-7/section-273.9#p-273.9(d)(6)(iii)(D)"
    )

    def formula(spm_unit, period, parameters):
        heating_type = spm_unit("heating_type", period)
        unspecified = heating_type == heating_type.possible_values.UNSPECIFIED
        incurs_heating = spm_unit("has_heating_expense", period)
        incurs_cooling = spm_unit("has_cooling_expense", period)
        # Deprecated legacy adapter: heating_cooling_expense was the only
        # heating/cooling signal before heating_type existed. It never read
        # heat_expense_included_in_rent, and that behavior is preserved for
        # unmigrated households.
        legacy_expense = spm_unit("heating_cooling_expense", period)
        legacy_incurs = unspecified & (legacy_expense > 0)
        return incurs_heating | incurs_cooling | legacy_incurs
