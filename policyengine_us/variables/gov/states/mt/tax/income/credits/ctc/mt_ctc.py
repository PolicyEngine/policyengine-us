from policyengine_us.model_api import *


class mt_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "MT CTC"
    definition_period = YEAR
    unit = USD
    documentation = "Montana Child Tax Credit"
    reference = "https://leg.mt.gov/bills/2023/billpdf/HB0268.pdf"
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.credits.ctc
        # income limit
        gross_income = tax_unit("adjusted_gross_income", period)
        income_eligible = gross_income <= p.income_threshold
        investment_income_eligible = (
            tax_unit("net_investment_income", period) <= p.investment_threshold
        )
        person = tax_unit.members
        dependent = person("is_tax_unit_dependent", period)
        meets_age_limit = person("age", period) < p.child_age_eligibility
        eligible_child = dependent & meets_age_limit

        eligible_children = tax_unit.any(eligible_child)

        eligible = income_eligible * investment_income_eligible

        child_amount = eligible_children * p.base
        credit = eligible * child_amount
        # reduction
        reduction_rate = p.reduction.rate * (
            max_((gross_income - p.reduction.threshold), 0)
            // p.reduction.increment
        )
        reduced_credit = max_((credit - reduction_rate), 0)

        return where(
            (gross_income > p.reduction.threshold), reduced_credit, credit
        )
