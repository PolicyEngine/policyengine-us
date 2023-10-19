from policyengine_us.model_api import *


class ky_pension_income_exclusion_exemption_eligible(Variable):
    value_type = bool
    entity = Person
    label = "KY Pension Income Exclusion Exemption Eligible"
    definition_period = YEAR
    defined_for = StateCode.KY
    reference = "https://revenue.ky.gov/Forms/Schedule%20P%202022.pdf"

    # Determine if person is eligible for exemption.
    # True if they retired from federal or KY government or receive railroad benefits.
    adds = [
        "retired_from_federal_government",
        "retired_from_ky_government",
        "railroad_benefits",
    ]
