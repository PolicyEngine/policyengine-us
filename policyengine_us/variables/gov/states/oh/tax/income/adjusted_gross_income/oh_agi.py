from policyengine_us.model_api import *


class oh_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5747.055",
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=20",
    )
    defined_for = StateCode.OH

    adds = [
        "adjusted_gross_income",
        "oh_bonus_depreciation_add_back",
        "oh_other_add_backs",
    ]

    subtracts = [
        "oh_section_179_expense_add_back",
        "qualified_business_income_deduction",
        "tax_unit_taxable_social_security",
        "dividend_income",
        # "above_the_line_deductions" #only need line 8z
        "oh_uniformed_services_retirement_income_deduction",
        "investment_in_529_plan",
        "pell_grant",
        "educator_expense",
        "disability_benefits",
    ]
