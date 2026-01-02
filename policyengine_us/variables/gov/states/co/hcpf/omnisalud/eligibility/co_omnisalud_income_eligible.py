from policyengine_us.model_api import *


class co_omnisalud_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets Colorado OmniSalud income eligibility"
    definition_period = YEAR
    defined_for = StateCode.CO
    reference = [
        "https://connectforhealthco.com/get-started/omnisalud/",
        "https://coloradoimmigrant.org/wp-content/uploads/2024/03/Eng.-OmniSalud-Guide-2024.pdf",
    ]
    documentation = """
    Colorado OmniSalud provides financial assistance (SilverEnhanced Savings)
    to individuals with income below 150% of the Federal Poverty Level.
    Those with higher income can still enroll but pay full premium.
    """

    def formula(person, period, parameters):
        p = parameters(period).gov.states.co.hcpf.omnisalud.eligibility
        # Use ACA MAGI as the income measure
        income_level = person("medicaid_income_level", period)

        return income_level < p.income_limit
