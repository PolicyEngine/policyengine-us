from policyengine_us.model_api import *


class hi_tip_income_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii qualified tips deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI
    reference = (
        "https://data.capitol.hawaii.gov/sessions/session2026/bills/HB2329_CD1_.pdf#page=1",
        "https://files.hawaii.gov/tax/news/announce/ann26-06.pdf#page=3",
        "https://www.law.cornell.edu/uscode/text/26/224",
    )

    def formula(tax_unit, period, parameters):
        if not parameters(
            period
        ).gov.states.hi.tax.income.deductions.tip_income.in_effect:
            return 0
        p = parameters(period).gov.irs.deductions.tip_income
        person = tax_unit.members
        tip_income = person("tip_income", period)
        occupation_requirement_met = person(
            "tip_income_deduction_occupation_requirement_met", period
        )
        qualified_tips = tax_unit.sum(tip_income * occupation_requirement_met)
        capped_tips = min_(p.cap, qualified_tips)
        # Section 224(b)(2) phases the deduction out with modified adjusted
        # gross income. HRS 235-1 defines adjusted gross income as determined
        # under the Internal Revenue Code as modified by chapter 235, so the
        # phase-out uses Hawaii adjusted gross income.
        hi_agi = tax_unit("hi_agi", period)
        filing_status = tax_unit("filing_status", period)
        agi_excess = max_(0, hi_agi - p.phase_out.start[filing_status])
        phase_out_amount = agi_excess * p.phase_out.rate
        deduction = max_(0, capped_tips - phase_out_amount)
        # Section 224(e) requires a social security number, and section 224(f)
        # requires married individuals to file a joint return.
        ssn_requirement_met = tax_unit(
            "tip_income_deduction_ssn_requirement_met", period
        )
        separate = filing_status == filing_status.possible_values.SEPARATE
        return where(ssn_requirement_met & ~separate, deduction, 0)
