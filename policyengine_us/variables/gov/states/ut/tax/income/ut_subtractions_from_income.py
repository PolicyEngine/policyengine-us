from policyengine_us.model_api import *


class ut_subtractions_from_income(Variable):
    """
    Line 8 on Utah 2022 Individual Income Tax return form TC-40. These
    subtractions from income include the following categories and are listed at
    https://incometax.utah.gov/subtractions with their accompanying codes.
    * 71: Interest from Utah municipal bonds and U. S. Government obligations
    * 77: Native American income
    * 78: Railroad retirement income
    * 79: Equitable adjustments
    * 82: Nonresident active duty military pay
    * 85: State tax refund distributed to beneficiary of trust
    * 88: Nonresident military spouse income
    * 89: FDIC premiums
    * 90: Qualified retirement plan distributions
    * SA: COVID-19 Utah grant funds included in AGI
    """

    value_type = float
    entity = TaxUnit
    label = "UT subtractions from income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT
