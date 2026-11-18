from policyengine_us.model_api import *
from policyengine_us.tools.mt_separate_return import mt_regular_tax


class mt_regular_income_tax_indiv(Variable):
    value_type = float
    entity = Person
    label = "Montana income (subtracting capital gains before 2024) tax before refundable credits, when married couples file separately"
    unit = USD
    definition_period = YEAR
    defined_for = "mt_married_filing_separately_on_same_return_eligible"

    def formula(person, period, parameters):
        taxable_income = person("mt_taxable_income_indiv", period)
        return mt_regular_tax(person, period, parameters, taxable_income)
