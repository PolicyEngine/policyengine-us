from policyengine_us.model_api import *


class ut_additions_to_income(Variable):
    """
    Utah additions to income are listed on the Income Tax Supplemental Schedule
    form TC-40A 2021 Part 1 (https://tax.utah.gov/forms/current/tc-40.pdf) with
    detailed codes at Utah Income Taxes: Additions to Income description page
    (https://incometax.utah.gov/additions). The codes include:
    51 - Lump Sum Distribution
    53 - Medical Care Savings Account (MSA) Addback
    54 - my529 Addback
    56 - Child's Income Excluded from Parent's Return
    57 - Municipal Bond Interest
    60 - Untaxed Income of a Resident Trust
    61 - Untaxed Income of a Nonresident Trust
    68 - Payroll Protection Program Grant or Loan Addback
    69 - Equitable Adjustments
    """

    value_type = float
    entity = TaxUnit
    label = "UT additions to income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT
