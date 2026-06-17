from policyengine_us.model_api import *


class mo_ccs_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Missouri Child Care Subsidy"
    definition_period = MONTH
    defined_for = StateCode.MO
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/5-CSR-25-200-060",
        "https://www.law.cornell.edu/regulations/missouri/5-CSR-25-200-050",
    )

    def formula(spm_unit, period, parameters):
        has_eligible_child = add(spm_unit, period, ["mo_ccs_eligible_child"]) > 0
        income_eligible = spm_unit("mo_ccs_income_eligible", period)
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        activity_eligible = spm_unit("mo_ccs_activity_eligible", period)
        protective = add(spm_unit, period, ["mo_ccs_protective_services"]) > 0
        # Protective-services children are eligible regardless of parental
        # financial need and are not subject to the income maximums or the need
        # for care, so the protective pathway bypasses both the income and
        # activity tests (5 CSR 25-200.060(7)(B)).
        return (
            has_eligible_child
            & asset_eligible
            & ((income_eligible & activity_eligible) | protective)
        )
