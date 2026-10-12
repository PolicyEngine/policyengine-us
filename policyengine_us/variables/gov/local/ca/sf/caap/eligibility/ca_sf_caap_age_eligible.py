from policyengine_us.model_api import *


class ca_sf_caap_age_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for San Francisco County CAAP due to age"
    definition_period = MONTH
    defined_for = "in_san_francisco"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.sf.caap.eligibility
        age = spm_unit.members("monthly_age", period)
        # CAAP serves adults; units with members under the age threshold are
        # CalWORKs-track instead (SEC. 20.7-6). We don't track the
        # CalWORKs-ineligibility-of-parents split at the moment, so we model the
        # adult-only requirement directly.
        #
        # The CAAP Manual (Div 91-4.5 Age, p.144) also admits some applicants
        # under 18 who are emancipated minors -- legally married, divorced,
        # widowed, registered domestic partners, or court-emancipated. We don't
        # track emancipation status at the moment (PolicyEngine has no
        # emancipated-minor input, and the constituent statuses for minors are
        # not separately modeled), so this rare exception pathway is not modeled;
        # the age gate applies the general 18-and-over rule.
        return spm_unit.all(age >= p.age_threshold)
