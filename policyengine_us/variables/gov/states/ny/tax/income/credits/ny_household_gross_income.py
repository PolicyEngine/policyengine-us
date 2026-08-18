from policyengine_us.model_api import *


class ny_household_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York IT-214 household gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY
    reference = "https://www.tax.ny.gov/pdf/current_forms/it/it214i.pdf#page=2"  # IT-214 Step 3, lines 9-16

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
