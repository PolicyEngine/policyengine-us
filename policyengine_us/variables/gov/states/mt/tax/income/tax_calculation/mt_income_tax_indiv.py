from policyengine_us.model_api import *


class mt_income_tax_indiv(Variable):
    value_type = float
    entity = Person
    label = "Montana income tax when married couples are filing separately"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        income_tax_before_credits = person(
            "mt_income_tax_before_refundable_credits_indiv", period
        )
        refundable_credits = person("mt_refundable_credits", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return head_or_spouse * (
            income_tax_before_credits - refundable_credits
        )
