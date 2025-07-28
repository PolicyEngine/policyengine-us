from policyengine_us.model_api import *


class overtime_income_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Overtime income deduction"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        overtime_income = person("fsla_overtime_premium", period)
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.irs.deductions.overtime_income_exempt
        cap = p.cap[filing_status]
        start = p.phase_out.start[filing_status]
        agi_excess = max_(agi - start, 0)
        phase_out_amount = agi_excess * p.phase_out.rate
        total_overtime_income = tax_unit.sum(overtime_income)
        capped_overtime_income = min_(cap, total_overtime_income)
        phased_out_overtime_income = max_(
            0, capped_overtime_income - phase_out_amount
        )
        ineligible_cardholder_present = tax_unit(
            "overtime_income_deduction_ineligible_cardholder_present", period
        )
        return phased_out_overtime_income * ~ineligible_cardholder_present
