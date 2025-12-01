from policyengine_us.model_api import *


class il_bcc_insurance_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Illinois BCC insurance eligible"
    documentation = "Eligible if person lacks health insurance that covers breast and cervical cancer treatment. This prevents double coverage - those with existing coverage should use their insurance."
    definition_period = YEAR
    reference = "https://www.dhs.state.il.us/page.aspx?item=33528"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # If already covered by Medicaid or Medicare, not BCC eligible
        on_medicaid = person("is_medicaid_eligible", period)
        on_medicare = person("is_medicare_eligible", period)
        # If paying health insurance premiums, likely has cancer coverage
        has_private_insurance = person("health_insurance_premiums", period) > 0
        has_coverage = on_medicaid | on_medicare | has_private_insurance
        return ~has_coverage
