from policyengine_us.model_api import *


class sc_obbba_addback(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina federal non-conformity addition for the One Big Beautiful Bill Act"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC
    reference = (
        "https://dor.sc.gov/income-tax-south-carolina-internal-revenue-code-conformity-update",
        "https://dor.sc.gov/sites/dor/files/forms/SC1040_2025.pdf",
        "https://dor.sc.gov/sites/dor/files/forms/SC1040Instr_2025.pdf#page=5",
    )

    def formula(tax_unit, period, parameters):
        # SC has not conformed to the One Big Beautiful Bill Act
        # (signed July 4, 2025). SC1040 line e adds back federal
        # deductions SC does not recognize.
        p = parameters(period).gov.states.sc.tax.income.additions.obbba
        filing_status = tax_unit("filing_status", period)
        itemizes = tax_unit("tax_unit_itemizes", period)
        federal_std_ded = parameters(period).gov.irs.deductions.standard.amount[
            filing_status
        ]
        pre_obbba_std_ded = p.pre_obbba_standard_deduction[filing_status]
        # Only taxpayers who used the standard deduction federally
        # add back the OBBBA-driven portion of it.
        std_ded_addback = where(
            itemizes, 0, max_(federal_std_ded - pre_obbba_std_ded, 0)
        )
        # Schedule 1-A deductions SC does not adopt.
        senior_deduction = tax_unit("additional_senior_deduction", period)
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
