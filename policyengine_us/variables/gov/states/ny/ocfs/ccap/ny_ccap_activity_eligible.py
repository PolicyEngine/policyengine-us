from policyengine_us.model_api import *


class ny_ccap_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for New York CCAP based on the reason for care"
    definition_period = MONTH
    defined_for = StateCode.NY
    documentation = (
        "New York grants the public-assistance reason-for-care route when a "
        "caretaker participates in a required activity under 18 NYCRR "
        "415.2(a)(1). Family Assistance, Safety Net Assistance and veteran "
        "assistance qualify as public assistance. Work, full-time study and "
        "meets_ccdf_activity_test provide the other activity routes. For the "
        "calculated work route, each tax-unit head or spouse must work or "
        "study, and the unit must contain a caretaker. PolicyEngine counts "
        "any positive weekly hours and retains the full-time-student "
        "approximation. OCFS sets the minimum work hours outside Part 415; "
        "public assistance recipients follow district work definitions. "
        "PolicyEngine has no input for a pending public assistance "
        "application, although applicants may also qualify for guaranteed "
        "care. The fallback input records job search, training, domestic "
        "violence services, substance abuse treatment, incapacity and family "
        "duties away from home."
    )
    reference = (
        "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=13",
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-415.2",
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-415.1",
        "https://www.nysenate.gov/legislation/laws/SOS/2",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_caretaker = person("is_tax_unit_head_or_spouse", period.this_year)
        hours = person("weekly_hours_worked_before_lsr", period.this_year)
        in_activity = (hours > 0) | person("is_full_time_student", period.this_year)
        has_caretaker = spm_unit.sum(is_caretaker) > 0
        every_caretaker_active = spm_unit.sum(is_caretaker & ~in_activity) == 0
        work_eligible = has_caretaker & every_caretaker_active
        # Reported receipt avoids the CCAP -> TANF -> child care expense cycle.
        public_assistance = (
            spm_unit("is_tanf_enrolled", period)
            | spm_unit("ny_safety_net_assistance_received", period)
            | spm_unit("ny_veteran_assistance_received", period)
        )
        required_activity = spm_unit("ny_ccap_required_activity", period)
        fallback = spm_unit("meets_ccdf_activity_test", period.this_year)
        return work_eligible | (public_assistance & required_activity) | fallback
