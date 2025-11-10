from policyengine_us.model_api import *


class mi_tanf_gross_unearned_income(Variable):
    value_type = float
    entity = Person
    label = "Michigan FIP gross unearned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/503.pdf",
        "https://www.michigan.gov/mdhhs/-/media/Project/Websites/mdhhs/Inside-MDHHS/Reports-and-Statistics---Human-Services/State-Plans-and-Federal-Regulations/TANF_State_Plan_2023.pdf",
    )
    defined_for = StateCode.MI

    def formula(person, period, parameters):
        # BEM 503 defines countable unearned income sources
        # Simplified implementation includes major sources
        COMPONENTS = [
            "social_security_disability",
            "social_security_retirement",
            "unemployment_compensation",
            "pension_income",
        ]
        return add(person, period, COMPONENTS)
