from policyengine_us.model_api import *


class tip_income_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tip income deduction"
    unit = USD
    definition_period = YEAR
    defined_for = "tip_income_deduction_ssn_requirement_met"

    def formula(tax_unit, period, parameters):
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
        phase_out_amount = magi_excess * p.phase_out.rate
        qualified_tip_income = tip_income * occupation_requirement_met
        total_tip_income = tax_unit.sum(qualified_tip_income)
        capped_tip_income = min_(p.cap, total_tip_income)
        return max_(0, capped_tip_income - phase_out_amount)
