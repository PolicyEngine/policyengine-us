from policyengine_us.model_api import *


class mt_income_tax_before_non_refundable_credits_indiv(Variable):
    value_type = float
    entity = Person
    label = "Montana income tax before refundable credits when married couples file separately"
    unit = USD
    definition_period = YEAR
    defined_for = "mt_married_filing_separately_on_same_return_eligible"

    adds = ["mt_capital_gains_tax_indiv", "mt_regular_income_tax_indiv"]
