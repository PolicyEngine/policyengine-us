from policyengine_us.model_api import *


class mt_income_tax_joint(Variable):
    value_type = float
    entity = Person
    label = "Montana income tax when married couples are filing jointly"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        income_tax_before_credits = add(
            person.tax_unit,
            period,
            ["mt_income_tax_before_refundable_credits_joint"],
        )
        refundable_credits = add(
            person.tax_unit, period, ["mt_refundable_credits"]
        )
        is_head = person("is_tax_unit_head", period)
        return is_head * (income_tax_before_credits - refundable_credits)
