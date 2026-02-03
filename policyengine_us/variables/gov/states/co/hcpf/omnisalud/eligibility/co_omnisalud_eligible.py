from policyengine_us.model_api import *


class co_omnisalud_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Colorado OmniSalud"
    definition_period = YEAR
    defined_for = StateCode.CO
    reference = [
        "https://connectforhealthco.com/get-started/omnisalud/",
        "https://coloradoimmigrant.org/wp-content/uploads/2024/03/Eng.-OmniSalud-Guide-2024.pdf",
    ]
    documentation = """
    Colorado OmniSalud provides marketplace coverage with premium subsidies
    to individuals who are ineligible for Health First Colorado (Medicaid),
    CHP+, or federal ACA subsidies due to their immigration status.
    """

    def formula(person, period, parameters):
        p = parameters(period).gov.states.co.hcpf.omnisalud.eligibility

        # Program must be in effect
        in_effect = p.in_effect

        # Must have eligible immigration status (undocumented, DACA before 2025)
        immigration_eligible = person(
            "co_omnisalud_immigration_status_eligible", period
        )

        # Must meet income requirements for financial assistance
        income_eligible = person("co_omnisalud_income_eligible", period)

        # Must not be eligible for other coverage
        # (Medicaid/CHP+ eligibility already checked via immigration status)

        return in_effect & immigration_eligible & income_eligible
