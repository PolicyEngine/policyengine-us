from policyengine_us.model_api import *


class va_low_income_tax_credit_agi_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Virginia low income tax credit"
    documentation = (
        "Whether family Virginia adjusted gross income is at or below the "
        "poverty guideline (Va. Code 58.1-339.8(B)(1)). Family Virginia "
        "adjusted gross income combines the Virginia adjusted gross income of "
        "the filer, the spouse and every dependent claimed on the return "
        "(58.1-339.8(A)). va_agi holds the filers' part. The model has no "
        "Virginia return for a dependent, so each dependent's federal "
        "adjusted gross income on their own return "
        "(dependent_adjusted_gross_income) stands in for their Virginia "
        "adjusted gross income."
    )
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacode/title58.1/chapter3/section58.1-339.8/",
        # Line 10, Compute your Family VAGI.
        "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2025-760-instructions.pdf#page=31",
    )
    defined_for = "va_low_income_tax_credit_eligible"

    def formula(tax_unit, period, parameters):
        filer_agi = tax_unit("va_agi", period)
        # Federal AGI, and so va_agi, leaves out a dependent's own income.
        dependent_agi = add(tax_unit, period, ["dependent_adjusted_gross_income"])
        family_agi = filer_agi + dependent_agi
        # Virginia does not account for blind or aged exemptions
        fpg = tax_unit("tax_unit_fpg", period)
        return family_agi <= fpg
