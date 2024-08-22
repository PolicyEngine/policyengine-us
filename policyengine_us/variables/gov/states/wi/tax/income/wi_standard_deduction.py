from policyengine_us.model_api import *


class wi_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin standard deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdf"
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdf"
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf"
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdf"
        "https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf"
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        fstatus = tax_unit("filing_status", period)
        deduction = parameters(period).gov.states.wi.tax.income.deductions
        max_amount = deduction.standard.max[fstatus]
        agi = tax_unit("wi_agi", period)
        phase_out_amount = select(
            [
                fstatus == fstatus.possible_values.SINGLE,
                fstatus == fstatus.possible_values.JOINT,
                fstatus == fstatus.possible_values.SURVIVING_SPOUSE,
                fstatus == fstatus.possible_values.SEPARATE,
                fstatus == fstatus.possible_values.HEAD_OF_HOUSEHOLD,
            ],
            [
                deduction.standard.phase_out.single.calc(agi),
                deduction.standard.phase_out.joint.calc(agi),
                deduction.standard.phase_out.joint.calc(agi),
                deduction.standard.phase_out.separate.calc(agi),
                deduction.standard.phase_out.head_of_household.calc(agi),
            ],
        )
        return max_(0, max_amount - phase_out_amount)
