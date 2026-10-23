from policyengine_us.model_api import *


class tip_income_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tip income deduction"
    unit = USD
    definition_period = YEAR
    defined_for = "tip_income_deduction_ssn_requirement_met"
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/224",
        "https://www.irs.gov/pub/irs-pdf/f1040s1a.pdf#page=1",
    )

    def formula(tax_unit, period, parameters):
        # Section 224 applies to taxable years beginning after December 31,
        # 2024, and 224(h) allows no deduction for any taxable year beginning
        # after December 31, 2028.
        if not parameters(period).gov.irs.deductions.tip_income.in_effect:
            return 0
        person = tax_unit.members
        tip_income = person("tip_income", period)
        occupation_requirement_met = person(
            "tip_income_deduction_occupation_requirement_met", period
        )
        # 26 U.S.C. 224(b)(2)(B): modified adjusted gross income adds back
        # income excluded under sections 911, 931 and 933.
        magi = tax_unit("agi_plus_section_911_931_933_exclusions", period)
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.irs.deductions.tip_income
        start = p.phase_out.start[filing_status]
        magi_excess = max_(magi - start, 0)
        # 26 U.S.C. 224(b)(2)(A): $100 for each $1,000 of excess. Schedule
        # 1-A, line 11, drops any fraction of a $1,000 increment.
        increments = np.floor(magi_excess / p.phase_out.increment)
        phase_out_amount = increments * p.phase_out.increment * p.phase_out.rate
        qualified_tip_income = tip_income * occupation_requirement_met
        total_tip_income = tax_unit.sum(qualified_tip_income)
        capped_tip_income = min_(p.cap, total_tip_income)
        deduction = max_(0, capped_tip_income - phase_out_amount)
        # 26 U.S.C. 224(f): a married individual takes the deduction only on
        # a joint return. Spouses considered unmarried under section 7703(b)
        # file as head of household and keep it.
        separate = filing_status == filing_status.possible_values.SEPARATE
        return where(separate, 0, deduction)
