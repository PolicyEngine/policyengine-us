from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_mt_ctc() -> Reform:
    class mt_ctc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Montana Child Tax Credit"
        definition_period = YEAR
        unit = USD
        reference = "https://leg.mt.gov/bills/2023/billpdf/HB0268.pdf"
        defined_for = "mt_ctc_eligible"

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.mt.ctc
            person = tax_unit.members
            age = person("age", period)
            credit_amount = tax_unit.sum(p.amount.calc(age))
            # Credit gets reduced by an amount for each increment that AGI exceeds a certain threshold
            agi = tax_unit("adjusted_gross_income", period)
            excess = max_(agi - p.reduction.threshold, 0)
            increments = excess // p.reduction.increment
            reduction = p.reduction.amount * increments
            return max_(credit_amount - reduction, 0)

    class mt_ctc_eligible(Variable):
        value_type = bool
        entity = TaxUnit
        label = "Eligible for the Montana Child Tax Credit"
        definition_period = YEAR
        reference = "https://leg.mt.gov/bills/2023/billpdf/HB0268.pdf"
        defined_for = StateCode.MT

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.mt.ctc.income_limit
            agi = tax_unit("adjusted_gross_income", period)
            agi_eligible = agi <= p.agi
            # CTC limited to filers with investment income below a certain threshold
            investment_income_eligible = (
                tax_unit("eitc_relevant_investment_income", period)
                < p.investment
            )

            earned_income = tax_unit("tax_unit_earned_income", period)
            receives_earned_income = earned_income > 0

            return (
                agi_eligible
                & investment_income_eligible
                & receives_earned_income
            )

    def modify_parameters(parameters):
        parameters.gov.states.mt.tax.income.credits.refundable.update(
            start=instant("2023-01-01"),
            stop=instant("2031-12-31"),
            value=["mt_ctc", "mt_eitc"],
        )
        return parameters

    class reform(Reform):
        def apply(self):
            self.update_variable(mt_ctc)
            self.update_variable(mt_ctc_eligible)
            self.modify_parameters(modify_parameters)

    return reform


def create_mt_ctc_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_mt_ctc()

    p = parameters.gov.contrib.states.mt.ctc

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_mt_ctc()
    else:
        return None


mt_ctc = create_mt_ctc_reform(None, None, bypass=True)
