from policyengine_us.model_api import *


class nd_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for North Dakota LIHEAP regular heating assistance"
    reference = (
        "https://www.nd.gov/dhs/policymanuals/415/415_20_10.htm",
        "https://www.nd.gov/dhs/policymanuals/415/415_20_10_30.htm",
        "https://www.nd.gov/dhs/policymanuals/415/415_20_10_50.htm",
    )
    defined_for = StateCode.ND

    def formula(spm_unit, period, parameters):
        heating_type = spm_unit("heating_type", period)
        types = heating_type.possible_values
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit("receives_housing_assistance", period)
        responsibility = heat_in_rent | (spm_unit("heating_expense", period) > 0)
        # Residence is approximated by state/SPMUnit membership. Institutional,
        # transient-residence and tribal election/duplicate-aid facts are not
        # available; households are assumed to use the state program.
        return (
            (spm_unit("nd_liheap_household_size", period) > 0)
            & (spm_unit("nd_liheap_share", period) > 0)
            & (heating_type != types.NONE)
            & responsibility
            & ~(heat_in_rent & subsidized)
        )
