from policyengine_us.model_api import *


class va_low_income_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Virginia Low Income Tax Credit"
    definition_period = YEAR
    defined_for = StateCode.VA
    reference = (
        "https://law.lis.virginia.gov/vacode/title58.1/chapter3/section58.1-339.8/",
        "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2025-760-instructions.pdf#page=30",
    )

    def formula(tax_unit, period, parameters):
        # Beyond its poverty test (va_low_income_tax_credit_agi_eligible), the
        # low-income credit has only the conditions Va. Code 58.1-339.8 sets
        # for every credit in the section.
        return tax_unit("va_eitc_eligible", period)
