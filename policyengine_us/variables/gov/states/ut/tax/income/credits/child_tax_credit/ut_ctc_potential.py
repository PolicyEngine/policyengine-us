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
        # Utah Code 59-10-1047(1)(d): modified adjusted gross income is the
        # claimant's and spouse's adjusted gross income, plus interest income
        # left out of it, plus the additions of Section 59-10-114. Nothing is
        # subtracted: the TC-40 worksheet starts from line 6 (total income),
        # before Utah subtractions and the state tax refund. Its line 4 takes
        # out the TC-40A code 57 addition (other states' municipal bond
        # interest) because line 6 adds all federal tax-exempt interest. The
        # model computes no such addition (ut_additions is the
        # ut_other_additions input alone), so ut_total_income plus
        # tax_exempt_interest_income counts that interest once, unless the
        # code 57 amount is also entered in ut_other_additions.
        relevant_income = tax_unit_non_dep_add(
            tax_unit,
            period,
            ["ut_total_income", "tax_exempt_interest_income"],
        )
        filing_status = tax_unit("filing_status", period)
        reduction_start = p.reduction.start[filing_status]
        excess_income = max_(relevant_income - reduction_start, 0)
        reduction = excess_income * p.reduction.rate
        return max_(base_amount - reduction, 0)
