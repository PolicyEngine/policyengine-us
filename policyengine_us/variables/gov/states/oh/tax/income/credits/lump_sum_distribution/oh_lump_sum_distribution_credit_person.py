from policyengine_us.model_api import *


class oh_lump_sum_distribution_credit_person(Variable):
    value_type = float
    entity = Person
    label = "Ohio lump sum distribution credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=29",
    )
    defined_for = "oh_lump_sum_distribution_credit_eligible_person"

    def formula(person, period, parameters):
        p_oh = parameters(
            period
        ).gov.states.oh.tax.income.credits.lump_sum_distribution
        p_us = parameters(period).gov.irs.credits.lump_sum_distribution
        age = person("age", period)
        return p_oh.base_amount * p_us.expected_remaining_years_of_life.calc(
            age
        )
