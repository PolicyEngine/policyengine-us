from policyengine_us.model_api import *


class mo_ccs_protective_services(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Missouri Child Care Subsidy protective services category"
    definition_period = MONTH
    defined_for = StateCode.MO
    reference = "https://www.law.cornell.edu/regulations/missouri/5-CSR-25-200-050"

    def formula(spm_unit, period, parameters):
        # Per 5 CSR 25-200.060(7)(A), the protective-services categories that
        # bypass the income maximums and the financial-need test are children
        # in DSS legal custody (proxied by foster care) and children receiving
        # or needing protective services. Homelessness is not a (7)(A) category;
        # it is a separate valid need for care (Manual 2010.050.35), so it is
        # handled in mo_ccs_activity_eligible and is still subject to the income
        # test.
        has_foster_child = add(spm_unit, period, ["is_in_foster_care"]) > 0
        has_protective_child = (
            add(
                spm_unit,
                period.this_year,
                ["receives_or_needs_protective_services"],
            )
            > 0
        )
        return has_foster_child | has_protective_child
