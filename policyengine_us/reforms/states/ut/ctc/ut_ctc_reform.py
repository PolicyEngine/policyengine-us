from policyengine_us.model_api import *
from policyengine_core.periods import instant
from policyengine_core.periods import period as period_


def create_ut_ctc() -> Reform:
    class ut_ctc_eligible_children(Variable):
        value_type = float
        entity = TaxUnit
        label = "Utah child tax credit eligible children"
        definition_period = YEAR
        defined_for = StateCode.UT

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.ut.tax.income.credits.ctc
            person = tax_unit.members
            ctc_eligible_child = person("ctc_qualifying_child", period)
            age = person("age", period)
            ut_child_age_eligible = p.child_age_threshold.calc(age)
            return tax_unit.sum(ctc_eligible_child & ut_child_age_eligible)

    class ut_ctc_potential(Variable):
        value_type = float
        entity = TaxUnit
        label = "Utah Child Tax Credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.UT

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ut.ctc
            eligible_children = tax_unit("ut_ctc_eligible_children", period)
            base_amount = p.amount * eligible_children
            relevant_income = add(
                tax_unit,
                period,
                ["tax_exempt_interest_income", "ut_taxable_income"],
            )
            filing_status = tax_unit("filing_status", period)
            reduction_start = p.reduction.start[filing_status]
            excess_income = max_(relevant_income - reduction_start, 0)
            baseline = parameters(period).gov.states.ut.tax.income.credits.ctc
            reduction = excess_income * baseline.reduction.rate
            return max_(base_amount - reduction, 0)

    class ut_refundable_ctc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Utah refundable child tax credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.UT

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ut.ctc
            potential = tax_unit("ut_ctc_potential", period)
            non_refundable = tax_unit("ut_ctc", period)
            eligible_children = tax_unit("ut_ctc_eligible_children", period)
            unused_credit = max_(potential - non_refundable, 0)
            refund_limit = p.refundable.amount * eligible_children
            return min_(unused_credit, refund_limit)

    def modify_parameters(parameters):
        refundable = parameters.gov.states.ut.tax.income.credits.refundable
        current_refundable = refundable(instant("2026-01-01"))
        if "ut_refundable_ctc" not in current_refundable:
            refundable.update(
                start=instant("2026-01-01"),
                stop=instant("2100-12-31"),
                value=list(current_refundable) + ["ut_refundable_ctc"],
            )
        return parameters

    class reform(Reform):
        def apply(self):
            self.update_variable(ut_ctc_eligible_children)
            self.update_variable(ut_ctc_potential)
            self.update_variable(ut_refundable_ctc)
            self.modify_parameters(modify_parameters)

    return reform


def create_ut_ctc_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_ut_ctc()

    p = parameters.gov.contrib.states.ut.ctc

    reform_active = False
    current_period = period_(period)

    for _ in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ut_ctc()
    else:
        return None


ut_ctc_reform = create_ut_ctc_reform(None, None, bypass=True)
