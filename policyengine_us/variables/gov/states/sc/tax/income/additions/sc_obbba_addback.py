from policyengine_us.model_api import *


class sc_obbba_addback(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina OBBBA non-conformity addition"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC
    reference = (
        "https://dor.sc.gov/sites/dor/files/forms/SC1040Instr_2025.pdf#page=3",
        "https://www.congress.gov/bill/119th-congress/house-bill/1/text",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.sc.tax.income.additions.obbba
        # SC does not conform to OBBBA provisions that reduce
        # federal taxable income. SC1040 line 2e adds back these
        # amounts.
        #
        # 1. OBBBA standard deduction increase.
        #    Only applies if taxpayer used the standard deduction.
        filing_status = tax_unit("filing_status", period)
        itemizes = tax_unit("tax_unit_itemizes", period)
        federal_std_ded = parameters(period).gov.irs.deductions.standard.amount[
            filing_status
        ]
        pre_obbba_std_ded = p.pre_obbba_standard_deduction[filing_status]
        std_ded_addback = where(
            itemizes, 0, max_(federal_std_ded - pre_obbba_std_ded, 0)
        )
        # 2. OBBBA senior deduction (entirely new from OBBBA).
        senior_deduction = tax_unit("additional_senior_deduction", period)
        # 3. Other OBBBA deductions (tip, overtime, auto loan).
        tip_deduction = tax_unit("tip_income_deduction", period)
        overtime_deduction = tax_unit("overtime_income_deduction", period)
        auto_loan_deduction = tax_unit("auto_loan_interest_deduction", period)
        return (
            std_ded_addback
            + senior_deduction
            + tip_deduction
            + overtime_deduction
            + auto_loan_deduction
        )
