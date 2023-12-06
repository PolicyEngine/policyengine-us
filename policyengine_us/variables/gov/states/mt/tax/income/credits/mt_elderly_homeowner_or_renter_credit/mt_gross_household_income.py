from policyengine_us.model_api import *


class mt_gross_household_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana gross household income for the elderly homeowner/renter credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    adds = "gov.states.mt.tax.income.credits.elderly_homeowner_or_renter_credit.gross_income_sources"
    # Tax form specifies total social social security - the taxable social security amounts
    # 2022 Montana Individual Income Tax Return, Line5: https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf#page=10
    subtracts = ["tax_exempt_social_security"]
