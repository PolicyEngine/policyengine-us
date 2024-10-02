from policyengine_us.model_api import *


class mt_elderly_homeowner_or_renter_credit_gross_household_income(Variable):
    value_type = float
    entity = Person
    label = "Montana gross household income for the elderly homeowner/renter credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    adds = "gov.states.mt.tax.income.credits.elderly_homeowner_or_renter.gross_income_sources"
