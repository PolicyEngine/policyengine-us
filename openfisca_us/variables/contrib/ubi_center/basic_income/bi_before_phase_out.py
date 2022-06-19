from openfisca_us.model_api import *


class bi_before_phase_out(Variable):
    value_type = float
    entity = Person
    label = "Basic income before phase-outs"
    unit = USD
    documentation = (
        "Total basic income payments for this person, before apply phase-outs."
    )
    definition_period = YEAR

    def formula(person, period, parameters):
        bi = parameters(period).contrib.ubi_center.basic_income
        age = person("age", period)
        return bi.amount_by_age.calc(age)
