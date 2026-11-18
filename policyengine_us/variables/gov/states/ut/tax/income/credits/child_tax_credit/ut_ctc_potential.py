from policyengine_us.model_api import *


class ut_ctc_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah Child Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1047.html",
        "https://www.law.cornell.edu/uscode/text/26/24#h_4_C",
        # 2025 TC-40 instructions, Child Tax Credit (code AT).
        "https://files.tax.utah.gov/tax/forms/2025/tc-40inst.pdf#page=24",
    )
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ut.tax.income.credits.ctc
        person = tax_unit.members
        # Utah Code 59-10-1047(1)(e) counts a child "with respect to whom the
        # claimant is allowed to claim a tax credit under Section 24". A child
        # whose filer fails the federal filer SSN rule of IRC 24(h)(7) gets
        # the credit for other dependents under IRC 24(h)(4)(C), so the child
        # still counts if the filer has an SSN or ITIN (IRC 24(e)(2)).
        child = person("ctc_qualifying_child_ignoring_filer_identification", period)
        filer_has_tin = person.tax_unit(
            "filer_meets_ctc_identification_requirements", period
        )
        ctc_eligible_child = child & filer_has_tin
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
