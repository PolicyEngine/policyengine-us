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
        return spm_unit.all(age >= p.age_threshold)
