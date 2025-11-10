from policyengine_us.model_api import *


class mi_tanf_gross_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Michigan FIP gross earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/518.pdf",
        "https://www.michigan.gov/mdhhs/-/media/Project/Websites/mdhhs/Inside-MDHHS/Reports-and-Statistics---Human-Services/State-Plans-and-Federal-Regulations/TANF_State_Plan_2023.pdf",
    )
    defined_for = StateCode.MI

    adds = ["employment_income", "self_employment_income"]
