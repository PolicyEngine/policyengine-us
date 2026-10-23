from policyengine_us.model_api import *


class overtime_income_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Overtime income deduction"
    unit = USD
    definition_period = YEAR
    defined_for = "overtime_income_deduction_ssn_requirement_met"
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/225",
        "https://www.irs.gov/pub/irs-pdf/f1040s1a.pdf#page=1",
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        overtime_income = person("fsla_overtime_premium", period)
        # 26 U.S.C. 225(b)(2)(B): modified adjusted gross income adds back
        # income excluded under sections 911, 931 and 933.
        magi = tax_unit("agi_plus_section_911_931_933_exclusions", period)
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.irs.deductions.overtime_income
        cap = p.cap[filing_status]
        start = p.phase_out.start[filing_status]
        magi_excess = max_(magi - start, 0)
        # 26 U.S.C. 225(b)(2)(A): $100 for each $1,000 of excess. Schedule
        # 1-A, line 19, drops any fraction of a $1,000 increment.
        increments = np.floor(magi_excess / p.phase_out.increment)
        phase_out_amount = increments * p.phase_out.increment * p.phase_out.rate
        total_overtime_income = tax_unit.sum(overtime_income)
        capped_overtime_income = min_(cap, total_overtime_income)
        deduction = max_(0, capped_overtime_income - phase_out_amount)
        # 26 U.S.C. 225(e): a married individual takes the deduction only on
        # a joint return. Spouses considered unmarried under section 7703(b)
        # file as head of household and keep it.
        separate = filing_status == filing_status.possible_values.SEPARATE
        return where(separate, 0, deduction)
