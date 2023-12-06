from policyengine_us.model_api import *


class oh_distribution_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio lump sum distribution credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=29",
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.oh.tax.income.credits
        age = person("age", period)
        amount = p.lump_sum_distribution.amount
        age_threshold = p.senior_citizen.age_threshold
        rate = p.lump_sum_distribution.rate.calc(age)
        return where(age >= age_threshold, amount * rate, 0)
