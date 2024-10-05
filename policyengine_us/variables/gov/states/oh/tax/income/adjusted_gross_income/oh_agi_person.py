from policyengine_us.model_api import *


class oh_agi_person(Variable):
    value_type = float
    entity = Person
    label = "Ohio adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5747.055",
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=20",
    )
    defined_for = StateCode.OH

    adds = ["adjusted_gross_income_person", "oh_additions"]

    subtracts = ["oh_deductions"]
