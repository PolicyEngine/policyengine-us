from policyengine_us.model_api import *


class csfp(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Commodity Supplemental Food Program"

    def formula(person, period, parameters):
        p = parameters(period).gov.usda.csfp
        income = person.spm_unit("wic_fpg", period)
        age = person("age", period)

        age_eligible = (age >= p.min_age)
        income_eligible = (income <= p.income_limit)

        eligible = age_eligible & income_eligible

        return eligible * p.amount
