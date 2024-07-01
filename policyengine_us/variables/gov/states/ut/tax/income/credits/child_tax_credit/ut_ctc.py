from policyengine_us.model_api import *


class ut_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah Child Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ut.tax.income.credits.ctc
        person = tax_unit.members
        ctc_eligible_child = person("ctc_qualifying_child", period)
        age = person("age", period)
        ut_child_age_eligible = p.child_age_threshold.calc(age)
        eligible_child = ctc_eligible_child & ut_child_age_eligible
        eligible_children = tax_unit.sum(eligible_child)
        base_amount = p.amount * eligible_children
        # Utah reduces the CTC based on the state income in addition to
        # tax exempt interest income
        relevant_income = add(
            tax_unit,
            period,
            ["tax_exempt_interest_income", "ut_taxable_income"],
        )
        filing_status = tax_unit("filing_status", period)
        reduction_start = p.reduction.start[filing_status]
        excess_income = max_(relevant_income - reduction_start, 0)
        reduction = excess_income * p.reduction.rate
        return max_(base_amount - reduction, 0)
