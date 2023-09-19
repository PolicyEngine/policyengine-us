from policyengine_us.model_api import *


class ky_pension_income_exclusion_exemption_eligible(Variable):
    value_type = bool
    entity = Person
    label = "KY Pension Income Exclusion Exemption Eligible"
    definition_period = YEAR
    defined_for = StateCode.KY
    reference = "https://revenue.ky.gov/Forms/Schedule%20P%202022.pdf"

    def formula(person, period, parameters):
        # Determine if person is eligible for exemption.
        # True if they retired from federal or KY government or receive railroad benefits.
        retired_from_fed_gov = person(
            "retired_from_federal_government", period
        )
        retired_from_ky_gov = person("retired_from_ky_government", period)
        receives_railroad_benefits = person(
            "receives_railroad_benefits", period
        )

        return (
            retired_from_fed_gov
            | retired_from_ky_gov
            | receives_railroad_benefits
        )
