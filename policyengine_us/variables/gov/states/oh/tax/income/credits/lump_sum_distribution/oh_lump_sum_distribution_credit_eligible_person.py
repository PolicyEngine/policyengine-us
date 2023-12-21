from policyengine_us.model_api import *


class oh_lump_sum_distribution_credit_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for the Ohio lump sum distribution credit"
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=29",
    )
    defined_for = StateCode.OH

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.oh.tax.income.credits.lump_sum_distribution
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        age = person("age", period)
        head_or_spouse_age = age * is_head_or_spouse
        return head_or_spouse_age >= p.age_threshold
