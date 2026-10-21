from policyengine_us.model_api import *


class hi_tanf_qualifying_incapacitated_adult_care_expenses(Variable):
    value_type = float
    entity = Person
    label = "Hawaii TANF qualifying incapacitated adult care expenses"
    documentation = (
        "Actual monthly cost of care for this person, when the person is an "
        "incapacitated adult who lives in the household and receives Hawaii "
        "TANF financial assistance (HAR 17-676-54.1(c)(4) and (d)(4)). Leave "
        "at zero for anyone who does not meet those conditions."
    )
    unit = USD
    definition_period = MONTH
    default_value = 0
    reference = (
        # PDF pages 36-37
        "https://humanservices.hawaii.gov/wp-content/uploads/2019/03/HAR-17-676-INCOME.pdf#page=36",
    )
