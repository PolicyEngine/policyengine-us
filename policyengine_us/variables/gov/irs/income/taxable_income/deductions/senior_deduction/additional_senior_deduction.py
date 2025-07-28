from policyengine_us.model_api import *


class additional_senior_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Senior deduction"
    unit = USD
    definition_period = YEAR
    defined_for = (
        "filer_meets_additional_senior_deduction_identification_requirements"
    )
    reference = "https://www.finance.senate.gov/imo/media/doc/finance_committee_legislative_text_title_vii.pdf#page=3"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions.senior_deduction
        aged_head = tax_unit("aged_head", period).astype(int)
        aged_spouse = tax_unit("aged_spouse", period).astype(int)
        aged_count = aged_spouse + aged_head
        base_deduction = p.amount * aged_count
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        phase_out_amount = where(
            joint,
            p.phase_out_rate.joint.calc(agi),
            p.phase_out_rate.other.calc(agi),
        )
        return max_(base_deduction - phase_out_amount, 0)
