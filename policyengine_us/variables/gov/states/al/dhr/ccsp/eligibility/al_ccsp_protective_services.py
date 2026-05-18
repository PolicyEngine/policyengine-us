from policyengine_us.model_api import *


class al_ccsp_protective_services(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Alabama CCSP protective services category"
    definition_period = MONTH
    defined_for = StateCode.AL
    reference = "https://dhr.alabama.gov/wp-content/uploads/2023/04/2025-2027-CCDF-State-Plan-with-Approval-Letter.pdf#page=23"

    def formula(spm_unit, period, parameters):
        # State Plan §2.2.2(f) names five protective-services sub-populations:
        # (i) foster care — modeled via is_in_foster_care
        # (ii) homelessness — modeled via is_homeless
        # (iii) families engaged with a child welfare agency — we don't
        #       track child-welfare engagement at the moment
        # (iv) Early Head Start Child Care Partnerships (EHS-CCP) — we
        #      don't track EHS-CCP enrollment at the moment
        # (v) kinship care / TANF-Other Relative (also a §3.3.1(vi) copay-
        #     waiver trigger) — we don't track kinship care at the moment
        # The three unmodeled categories under-count protective-services
        # eligibility, which waives the income and activity tests
        # (§2.2.2(g)-(h)).
        has_foster_child = add(spm_unit, period, ["is_in_foster_care"]) > 0
        is_homeless = spm_unit.household("is_homeless", period.this_year)
        return has_foster_child | is_homeless
