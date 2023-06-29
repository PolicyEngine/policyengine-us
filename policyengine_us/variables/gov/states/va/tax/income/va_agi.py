from policyengine_us.model_api import *


class va_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia Adjusted Gross Income (VAGI)"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
    )
    defined_for = StateCode.VA

    adds = [
        "adjusted_gross_income",
        "va_interest_on_obligations_of_other_states",
        "va_other_additions",
    ]
    subtracts = [
        "va_military_basic_pay_subtraction",
        "va_age_deduction",
        "va_disability_income_subtraction",
        "va_federal_state_employees_subtraction",
        "va_military_benefit_subtraction",
        "va_retirement_plan_taxed_subtraction",
        "va_unemployment_compensation_benefit_subtraction",
        "va_real_estate_investment_trust_subtraction",
    ]
