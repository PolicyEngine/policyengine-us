from policyengine_us.model_api import *


class ri_medicaid_has_third_party_coverage(Variable):
    value_type = bool
    entity = Person
    label = "Rhode Island Medicaid third-party health coverage"
    definition_period = YEAR
    defined_for = StateCode.RI
    reference = (
        "https://rules.sos.ri.gov/regulations/part/210-30-00-1",
        "https://eohhs.ri.gov/providers-partners/billing-and-claims/third-party-liability",
        "https://tricare.mil/FAQs/General/GEN_OHI_TRICARE",
        "https://www.va.gov/resources/champva-care/",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ri.eohhs.medicaid
        return add(person, period, p.third_party_coverage) > 0
