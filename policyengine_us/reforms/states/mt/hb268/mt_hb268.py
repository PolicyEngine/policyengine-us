from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_mt_hb268() -> Reform:
    class mt_hb268(Variable):
        value_type = float
        entity = Person
        label = "Montana HB268 Child Tax Credit"
        definition_period = YEAR
        unit = USD
        reference = "https://leg.mt.gov/bills/2023/billpdf/HB0268.pdf"
        defined_for = StateCode.MT

        def formula(person, period, parameters):
            eligible = person.tax_unit("mt_hb268_eligible", period)
            p = parameters(period).gov.contrib.states.mt.hb268
            # Only count qualifying children
            is_qualifying = person("ctc_qualifying_child", period)
            age = person("age", period)
            child_credit = p.amount.calc(age) * is_qualifying
            credit_amount = person.tax_unit.sum(child_credit)
            # Credit gets reduced by an amount for each increment that AGI exceeds a certain threshold
            agi = person.tax_unit("adjusted_gross_income", period)
            excess = max_(agi - p.reduction.threshold, 0)
            # Ceiling: any fraction of an increment triggers reduction
            increments = np.ceil(excess / p.reduction.increment)
            reduction = p.reduction.amount * increments
            credit = max_(credit_amount - reduction, 0)
            is_head = person("is_tax_unit_head", period)
            return is_head * eligible * credit

    class mt_hb268_eligible(Variable):
        value_type = bool
        entity = TaxUnit
        label = "Eligible for the Montana HB268 Child Tax Credit"
        definition_period = YEAR
        reference = "https://leg.mt.gov/bills/2023/billpdf/HB0268.pdf"
        defined_for = StateCode.MT

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.mt.hb268.income_limit
            # Per HB 268 Section 1(1), taxpayer must be "permitted a child
            # tax credit under section 24 of the Internal Revenue Code"
            federal_ctc_eligible = tax_unit("ctc_qualifying_children", period) > 0
            agi = tax_unit("adjusted_gross_income", period)
            agi_eligible = agi <= p.agi
            # CTC limited to filers with investment income below a certain threshold
            investment_income_eligible = (
                tax_unit("eitc_relevant_investment_income", period) < p.investment
            )

            earned_income = tax_unit("tax_unit_earned_income", period)
            receives_earned_income = earned_income > 0

            return (
                federal_ctc_eligible
                & agi_eligible
                & investment_income_eligible
                & receives_earned_income
            )

    def modify_parameters(parameters):
        parameters.gov.states.mt.tax.income.credits.refundable.update(
            start=instant("2023-01-01"),
            stop=instant("2031-12-31"),
            value=["mt_hb268", "mt_eitc"],
        )
        return parameters

    class reform(Reform):
        def apply(self):
            self.update_variable(mt_hb268)
            self.update_variable(mt_hb268_eligible)
            self.modify_parameters(modify_parameters)

    return reform


def create_mt_hb268_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_mt_hb268()

    p = parameters.gov.contrib.states.mt.hb268

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_mt_hb268()
    else:
        return None


mt_hb268 = create_mt_hb268_reform(None, None, bypass=True)
