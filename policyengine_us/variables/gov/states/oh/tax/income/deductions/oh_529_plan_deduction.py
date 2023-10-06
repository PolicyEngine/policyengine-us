from policyengine_us.model_api import *


class oh_529_plan_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio contributions to 529 plan deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=18",
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.oh.tax.income.deductions.plan_529_contributions
        contribution_amount = tax_unit("investment_in_529_plan", period)
        capped_amount = min_(contribution_amount, p.max_amount)
        return max_(capped_amount, 0)
