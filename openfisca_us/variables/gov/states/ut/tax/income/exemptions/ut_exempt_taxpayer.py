from openfisca_us.model_api import *


class ut_exempt_taxpayer(Variable):
    """
    Utah qualified exempt taxpayer is listed on the Utah Individual Income Tax
    Return form TC-40 2021 line 21
    (https://tax.utah.gov/forms/current/tc-40.pdf)
    """

    value_type = bool
    entity = TaxUnit
    label = "UT exempt taxpayer"
    unit = bool
    definition_period = YEAR
    reference = "https://incometax.utah.gov/filing/qualified-exempt-taxpayers"
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        federal_agi = tax_unit("adjusted_gross_income", period)
        standard_deduction = tax_unit("standard_deduction", period)
        ut_exempt_taxpayer = federal_agi - standard_deduction <= 0
        return ut_exempt_taxpayer
