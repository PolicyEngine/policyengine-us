from policyengine_us.model_api import *


class il_bcc_insurance_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Illinois BCC insurance eligible"
    definition_period = YEAR
    reference = "https://www.dhs.state.il.us/page.aspx?item=33528"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Eligible if not Medicaid eligible and no employer-sponsored insurance.
        # This prevents double coverage for those who already have health insurance.
        on_medicaid = person("is_medicaid_eligible", period)
        has_esi = person("has_esi", period)
        has_coverage = on_medicaid | has_esi
        return ~has_coverage
