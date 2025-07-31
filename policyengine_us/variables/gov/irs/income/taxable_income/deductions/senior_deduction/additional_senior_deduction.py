from policyengine_us.model_api import *


class additional_senior_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Senior deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.congress.gov/bill/119th-congress/house-bill/1/text"
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions.senior_deduction
        eligible_seniors = add(
            tax_unit,
            period,
            ["additional_senior_deduction_eligible_person"],
        )

        base_deduction = p.amount * eligible_seniors
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        phase_out_amount = where(
            joint,
            p.phase_out_rate.joint.calc(agi),
            p.phase_out_rate.other.calc(agi),
        )
        return max_(base_deduction - phase_out_amount, 0)
