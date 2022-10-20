from policyengine_us.model_api import *


class ut_subtractions_from_income(Variable):
    """
    Utah subtractions from income are listed on the Income Tax Supplemental
    Schedule form TC-40A 2021 Part 2
    (https://tax.utah.gov/forms/current/tc-40.pdf) with detailed codes at Utah
    Income Taxes: Subtractions from Income description page
    (https://incometax.utah.gov/subtractions). The codes include:
    71 - Interest from Utah Municipal Bonds and U. S. Government Obligations
    77 - Native American Income
    78 - Railroad Retirement Income
    79 - Equitable Adjustments
    82 - Nonresident Active Duty Military Pay
    85 - State Tax Refund Distributed to Beneficiary of Trust
    88 - Nonresident Military Spouse Income
    89 - FDIC Premiums
    90 - Qualified Retirement Plan Distributions
    SA - COVID-19 Utah Grant Funds Included in AGI
    """

    value_type = float
    entity = TaxUnit
    label = "UT subtractions from income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT
