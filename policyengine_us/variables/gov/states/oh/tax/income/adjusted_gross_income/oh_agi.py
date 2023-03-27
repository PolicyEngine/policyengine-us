from policyengine_us.model_api import *


class oh_agi(Variable):
    value_type = float
    entity = Person
    label = "Ohio adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=20",
        "https://codes.ohio.gov/ohio-revised-code/section-5747.055",
    )
    defined_for = StateCode.OH

    adds = ["adjusted_gross_income"]
    subtracts = [
        "oh_military_pay_outside_ohio_deduction",
        "oh_uniformed_services_retirement_income_deduction",
        "investment_in_529_plan",
        "pell_grant",
        "educator_expense",
        "disability_benefits",
    ]
