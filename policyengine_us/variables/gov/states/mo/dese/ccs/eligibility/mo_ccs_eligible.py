from policyengine_us.model_api import *


class mo_ccs_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Missouri Child Care Subsidy"
    definition_period = MONTH
    defined_for = StateCode.MO
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/5-CSR-25-200-060",
        "https://web.archive.org/web/20211208073247id_/https://dese.mo.gov/childhood/quality-programs/child-care-subsidy/child-care-manual/2010/005/00",
    )

    def formula(spm_unit, period, parameters):
        has_eligible_child = add(spm_unit, period, ["mo_ccs_eligible_child"]) > 0
        income_eligible = spm_unit("mo_ccs_income_eligible", period)
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        activity_eligible = spm_unit("mo_ccs_activity_eligible", period)
        protective = spm_unit("mo_ccs_protective_services", period)
        # The need for care is met by an activity or by the protective-services
        # pathway.
        return (
            has_eligible_child
            & income_eligible
            & asset_eligible
            & (activity_eligible | protective)
        )
