from policyengine_us.model_api import *


class ut_taxable_income(Variable):
    """
    Line 9 on Utah 2022 Individual Income Tax return form TC-40.
    """

    value_type = float
    entity = TaxUnit
    label = "UT taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT

    adds = ["ut_total_income"]
    subtracts = ["salt_refund_last_year", "ut_subtractions_from_income"]
