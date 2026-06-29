from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_nj_s4531() -> Reform:
    def s4531_amount(taxable_income, p):
        return select(
            [
                taxable_income <= p.income_limit.first,
                taxable_income <= p.income_limit.second,
                taxable_income <= p.income_limit.third,
                taxable_income <= p.income_limit.fourth,
                taxable_income <= p.income_limit.fifth,
            ],
            [
                p.amount.first,
                p.amount.second,
                p.amount.third,
                p.amount.fourth,
                p.amount.fifth,
            ],
            default=0,
        )

    class nj_ctc(Variable):
        value_type = float
        entity = TaxUnit
        label = "New Jersey Child Tax Credit"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.njleg.state.nj.us/bill-search/2026/S4531",
            "https://pub.njleg.gov/Bills/2026/S5000/4531_I1.PDF#page=2",
            "https://pub.njleg.gov/Bills/2026/S5000/4531_S1.PDF#page=1",
        )
        defined_for = "nj_ctc_eligible"

        def formula(tax_unit, period, parameters):
            p = parameters(period)
            p_baseline = p.gov.states.nj.tax.income.credits.ctc
            p_reform = p.gov.contrib.states.nj.s4531

            taxable_income = tax_unit("nj_taxable_income", period)
            if p_reform.in_effect and p_reform.temporary_increase.in_effect:
                amount_per_qualifying_child = s4531_amount(taxable_income, p_reform)
            else:
                amount_per_qualifying_child = p_baseline.amount.calc(taxable_income)

            person = tax_unit.members
            age_eligible = person("age", period) < p_baseline.age_limit
            dependent = person("is_tax_unit_dependent", period)
            count_eligible = tax_unit.sum(age_eligible & dependent)

            return count_eligible * amount_per_qualifying_child

    class reform(Reform):
        def apply(self):
            self.update_variable(nj_ctc)

    return reform


def create_nj_s4531_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_nj_s4531()

    p = parameters.gov.contrib.states.nj.s4531

    reform_active = False
    current_period = period_(period)

    for _ in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_nj_s4531()
    return None


nj_s4531_reform = create_nj_s4531_reform(None, None, bypass=True)
