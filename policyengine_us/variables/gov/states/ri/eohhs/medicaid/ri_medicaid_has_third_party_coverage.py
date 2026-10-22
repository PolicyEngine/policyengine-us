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
        return (
            add(
                person,
                period,
                [
                    "has_esi",
                    "has_marketplace_health_coverage_at_interview",
                    "has_non_marketplace_direct_purchase_health_coverage_at_interview",
                    "medicare_enrolled",
                    "has_tricare_health_coverage_at_interview",
                    "has_champva_health_coverage_at_interview",
                ],
            )
            > 0
        )
