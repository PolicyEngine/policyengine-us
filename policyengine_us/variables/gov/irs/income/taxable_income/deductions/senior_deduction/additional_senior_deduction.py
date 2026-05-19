from policyengine_us.model_api import *


class additional_senior_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Senior deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.congress.gov/119/bills/hr1/BILLS-119hr1enr.pdf#page=88",
        "https://www.irs.gov/pub/irs-pdf/f1040s1a.pdf#page=2",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions.senior_deduction
        eligible_seniors = add(
            tax_unit,
            period,
            ["additional_senior_deduction_eligible_person"],
        )

        magi = tax_unit("additional_senior_deduction_magi", period)
        filing_status = tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        phase_out_amount = where(
            joint,
            p.phase_out_rate.joint.calc(magi),
            p.phase_out_rate.other.calc(magi),
        )
        # Schedule 1-A applies the phase-out to each $6,000 amount
        # individually, then sums across eligible seniors.
        per_senior_allowed = max_(p.amount - phase_out_amount, 0)
        return per_senior_allowed * eligible_seniors
