from policyengine_us.model_api import *


class mt_pension_exemption_joint(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "Montana partial pension, annuity, and IRA income exemption on a joint return"
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2023_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=6",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=34",
    )
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.subtractions.pension.phase_out
        # Line 3b: a joint return adds the spouses' line 3a amounts.
        exemption = add(tax_unit, period, ["mt_pension_exemption_before_phase_out"])
        # Lines 4-6: the reduction applies once, to the joint federal
        # adjusted gross income.
        agi = tax_unit("adjusted_gross_income", period)
        reduction = p.rate * max_(agi - p.threshold, 0)
        # Line 7
        return max_(exemption - reduction, 0)
