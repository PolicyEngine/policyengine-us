from policyengine_us.model_api import *


class mn_k12_education_subtraction_qualifying_expenses_person(Variable):
    value_type = float
    entity = Person
    label = "Minnesota K-12 Education Subtraction qualifying expenses for this child"
    documentation = (
        "Expenses for this qualifying child that otherwise qualify for the "
        "Minnesota K-12 Education Subtraction, after excluding expenses used "
        "for the K-12 Education Credit. Once any qualifying child in the tax "
        "unit has a positive record, the subtraction uses only these records "
        "and ignores the tax unit's k12_tuition_and_fees, so the records must "
        "then cover every child."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290.0132#stat.290.0132.4",
        "https://www.revenue.state.mn.us/sites/default/files/2026-07/m1m-25.pdf#page=5",
    )
