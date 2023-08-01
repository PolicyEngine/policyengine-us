from policyengine_us.model_api import *


class mt_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana CTC"
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
        age = person("age", period)
        dependent = person("is_tax_unit_dependent", period)
        eligible = (age <= p.child_age_eligibility) & dependent

        eligible = income_eligible * investment_income_eligible

        credit = tax_unit.sum(p.base.calc(age) * eligible)

        # reduction
        excess = max_(gross_income - p.reduction.threshold, 0)
        increments = excess // p.reduction.increment
        reduction_rate = p.reduction.rate * increments

        return max_(credit - reduction_rate, 0)
