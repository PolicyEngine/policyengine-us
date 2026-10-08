from policyengine_us.model_api import *


class mt_federal_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal deductions for Montana Form 2 line 2"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = (
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2024_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=15",
        "https://revenue.mt.gov/files/Forms/SALT-Cap-Instructions.pdf#page=1",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2025_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=1",
    )

    def formula(tax_unit, period, parameters):
        deductions = tax_unit("taxable_income_deductions", period)
        # The instructions exclude QBI from line 2, implementing the
        # addition required by MCA 15-30-2120(2)(i). The federal deduction
        # type and Schedule 1-A / non-itemizer charitable deductions flow
        # through taxable_income_deductions.
        qbi = tax_unit("qualified_business_income_deduction", period)
        p = parameters(period).gov.states.mt.tax.income.additions
        if p.state_income_tax_reduces_federal_deduction:
            return deductions - qbi - tax_unit("mt_state_income_tax_addback", period)
        return deductions - qbi
