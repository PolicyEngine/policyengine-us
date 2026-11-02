from policyengine_us.model_api import *


class mn_k12_education_subtraction_higher_cap_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Attended grades 7 to 12 for the Minnesota K-12 Education Subtraction"
    documentation = (
        "Whether this qualifying child attended grades 7 to 12 during the "
        "tax year, so the higher per-child cap applies."
    )
    definition_period = YEAR
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290.0132#stat.290.0132.4",
        "https://www.revenue.state.mn.us/sites/default/files/2026-07/m1m-25.pdf#page=5",
    )
