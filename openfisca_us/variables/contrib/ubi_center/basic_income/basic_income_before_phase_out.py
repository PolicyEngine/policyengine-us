from openfisca_us.model_api import *


class basic_income_before_phase_out(Variable):
    value_type = float
    entity = Person
    label = "Basic income before phase-outs"
    unit = USD
    documentation = (
        "Total basic income payments for this person, before phasing out."
    )
    definition_period = YEAR

    def formula(person, period, parameters):
        p = parameters(period).contrib.ubi_center.basic_income
        age = person("age", period)
        return p.amount_by_age.calc(age)
