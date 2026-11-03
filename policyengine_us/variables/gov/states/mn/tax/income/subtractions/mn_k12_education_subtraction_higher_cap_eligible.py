from policyengine_us.model_api import *


class mn_k12_education_subtraction_higher_cap_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Attended grades 7 to 12 for the Minnesota K-12 Education Subtraction"
    documentation = (
        "Whether this qualifying child's grade at the end of the tax year "
        "falls in 7 to 12, or the child finished grade 12 and started college "
        "during the year, so the higher per-child cap applies. Without an "
        "input, the formula places children aged 12 or older in grades 7 to "
        "12, reading is_in_k12_school's ages 5 to 17 as kindergarten (age 5) "
        "to grade 12 (age 17)."
    )
    definition_period = YEAR
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290.0132#stat.290.0132.4",
        "https://www.revenue.state.mn.us/k-12-education-subtraction-and-credit",
        "https://www.revenue.state.mn.us/k-12-education-subtraction-and-credit-0",
        "https://www.revenue.state.mn.us/sites/default/files/2026-07/m1m-25.pdf#page=5",
    )

    def formula(person, period, parameters):
        # An imputation, not policy, so it has no parameter (as in
        # is_in_k12_school): grade = age - 5, so grade 7 is age 12.
        return person("age", period) >= 12
