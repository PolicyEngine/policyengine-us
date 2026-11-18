from policyengine_us.model_api import *


class oh_529_plan_deduction_person(Variable):
    value_type = float
    entity = Person
    label = "Ohio deduction for contributions to 529 plans"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5747.70",
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=18",
    )
    defined_for = StateCode.OH

    def formula(person, period, parameters):
        # Allocate the return's deduction among the filer contributors.
        filer = ~person("is_tax_unit_dependent", period)
        contribution_amount = person("investment_in_529_plan_indv", period) * filer
        total_contributions = person.tax_unit.sum(contribution_amount)
        total_deduction = person.tax_unit("oh_529_plan_deduction", period)
        contributions_rate = np.zeros_like(total_contributions)
        mask = total_contributions != 0
        contributions_rate[mask] = contribution_amount[mask] / total_contributions[mask]
        return contributions_rate * total_deduction
