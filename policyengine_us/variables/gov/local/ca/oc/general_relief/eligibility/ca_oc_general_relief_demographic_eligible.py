from policyengine_us.model_api import *


class ca_oc_general_relief_demographic_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets Orange County General Relief demographic requirements"
    definition_period = MONTH
    defined_for = "in_oc"
    reference = "https://www.ssa.ocgov.com/cash-calfresh/faqs/general-relief"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.oc.general_relief.eligibility
        age = spm_unit.members("monthly_age", period)
        return spm_unit.all(age >= p.adult_age_threshold)
