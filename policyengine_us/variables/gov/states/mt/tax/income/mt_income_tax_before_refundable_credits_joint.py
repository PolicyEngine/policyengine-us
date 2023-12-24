from policyengine_us.model_api import *


class mt_income_tax_before_refundable_credits_joint(Variable):
    value_type = float
    entity = Person
    label = "Montana income tax before refundable credits when married couples are filing jointly"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        income_before_credits = add(person.tax_unit, period,["mt_income_tax_before_non_refundable_credits_joint"])
        non_refundable_credits = person("mt_non_refundable_credits", period)
        head = person("is_tax_unit_head", period)
        return head * max_(income_before_credits - non_refundable_credits, 0)
