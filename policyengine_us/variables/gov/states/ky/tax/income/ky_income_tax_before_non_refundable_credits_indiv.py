from policyengine_us.model_api import *


class ky_income_tax_before_non_refundable_credits_indiv(Variable):
    value_type = float
    entity = Person
    label = "Kentucky income tax before non-refundable credits when married couples are filing separately"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(person, period, parameters):
        ky_taxable_income_indiv = person("ky_taxable_income_indiv", period)
        p = parameters(period).gov.states.ky.tax.income
        return ky_taxable_income_indiv * p.rate
