from policyengine_us.model_api import *


class additional_senior_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Additional senior deduction"
    unit = USD
    definition_period = YEAR
    defined_for = (
        "filer_meets_additional_senior_deduction_identification_requirements"
    )
    reference = "https://punchbowl.news/smitmo_017_xml/"  # page 35

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.contrib.reconciliation.additional_senior_standard_deduction
        aged_head = tax_unit("aged_head", period).astype(int)
        aged_spouse = tax_unit("aged_spouse", period).astype(int)
        aged_count = aged_spouse + aged_head
        base_deduction = p.amount * aged_count
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        phase_out_amount = where(
            joint, p.rate.joint.calc(agi), p.rate.other.calc(agi)
        )
        return max_(base_deduction - phase_out_amount, 0)
