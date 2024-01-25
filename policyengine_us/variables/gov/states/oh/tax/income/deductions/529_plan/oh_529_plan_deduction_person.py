from policyengine_us.model_api import *


class oh_529_plan_deduction_person(Variable):
    value_type = float
    entity = Person
    label = "Ohio deduction for contributions to 529 plans"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=18",
    )
    defined_for = StateCode.OH

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.oh.tax.income.deductions.plan_529_contributions
        contribution_amount = person("investment_in_529_plan_indv", period)
        beneficiaries = person("count_529_contribution_beneficiaries", period)
        total_beneficiaries = person.tax_unit.sum(beneficiaries)
        cap = p.cap * total_beneficiaries
        total_contributions = person.tax_unit.sum(contribution_amount)
        return min_(total_contributions, cap)
