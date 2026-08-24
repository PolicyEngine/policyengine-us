from policyengine_us.model_api import *


class ny_household_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York IT-214 household gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY
    documentation = (
        "IT-214 household gross income (Step 3, line 16) is the eligibility "
        "and credit-sizing income measure through tax year 2024; from 2025 the "
        "credit uses federal AGI instead (see ny_real_property_tax_credit). By "
        "statute (Tax Law 606(e)(1)(C)) household gross income is the income of "
        "ALL household members; this variable sums at the tax unit as a "
        "simplification. It also omits statutory line items PolicyEngine does "
        "not yet add back here: pensions and annuities not in AGI (line 13), "
        "cash public assistance and TANF (line 14), workers' compensation, "
        "child support / support money, and veterans' disability pensions "
        "(line 11)."
    )
    # Year-specific 2024 instructions; the current_forms/ URL resolves to the
    # latest (2025) form, whose Step 3 uses federal AGI, not this measure.
    reference = "https://www.tax.ny.gov/pdf/2024/inc/it214i_2024.pdf#page=2"  # IT-214 Step 3, lines 9-16

    def formula(tax_unit, period, parameters):
        # Form IT-214, Step 3 "Determine household gross income" (line 16 =
        # sum of lines 9 through 15). Line 9 is federal AGI; the remaining
        # lines add income that is not already in AGI, "even if not taxable."
        agi = tax_unit("adjusted_gross_income", period)  # line 9
        person = tax_unit.members
        # Line 11: Social Security payments not included on line 9 (i.e. the
        # portion of benefits not taxed federally). Line 11 instructions:
        # "including all payments received under the Social Security Act."
        social_security = person("social_security", period)
        taxable_social_security = person("taxable_social_security", period)
        nontaxable_social_security = max_(social_security - taxable_social_security, 0)
        # Line 12: Supplemental Security Income (SSI).
        ssi = person("ssi", period)
        # Line 15: other income (tax-exempt interest).
        tax_exempt_interest = person("tax_exempt_interest_income", period)
        additions = tax_unit.sum(nontaxable_social_security + ssi + tax_exempt_interest)
        return agi + additions
