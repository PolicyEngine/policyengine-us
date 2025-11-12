from policyengine_us.model_api import *


class tn_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Tennessee TANF eligible"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/tennessee/Tenn-Comp-R-Regs-1240-01-50",
        "Tennessee Administrative Code § 1240-01-50 - Financial Eligibility Requirements",
        "https://www.tn.gov/humanservices/for-families/families-first-tanf/families-first-eligibility-information.html",
    )
    defined_for = StateCode.TN

    def formula(spm_unit, period, parameters):
        # Must meet income eligibility
        income_eligible = spm_unit("tn_tanf_income_eligible", period)

        # Must meet resource eligibility
        resources_eligible = spm_unit("tn_tanf_resources_eligible", period)

        # Must have a child under age limit (or at age limit and in high school)
        p = parameters(period).gov.states.tn.dhs.tanf.eligibility
        person = spm_unit.members
        age = person("age", period)
        child_age_limit = p.child_age_limit
        has_qualifying_child = spm_unit.any(age < child_age_limit)

        # Combine all eligibility criteria
        return income_eligible & resources_eligible & has_qualifying_child
