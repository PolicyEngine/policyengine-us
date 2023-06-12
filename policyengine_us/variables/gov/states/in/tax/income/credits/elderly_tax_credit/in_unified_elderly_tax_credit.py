from policyengine_us.model_api import *


class in_unified_elderly_tax_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana unified elderly tax credit income"
    unit = USD
    definition_period = YEAR
    documention = "Income that is utilized for the elderly credit calculation"
    reference = "https://forms.in.gov/Download.aspx?id=15394 "
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        income = person("in_unified_elderly_tax_income", period)
        total_income = tax_unit.sum(income)
        age_head = tax_unit("age_head", period)
        spouse_age = tax_unit("age_spouse", period)
