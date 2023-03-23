from policyengine_us.model_api import *


class ut_apportionable_nonrefundable_credits(Variable):
    """
    Line 24 on Utah 2022 Individual Income Tax return form TC-40. These
    credits include the following categories and are listed at
    https://incometax.utah.gov/credits with their accompanying codes.
    * 04: Capital gain transactions credit
    * 18: Retirement credit
    * 20: Utah my529 credit
    * 23: Health benefit plan credit
    * 26: Gold and silver coin sale credit
    * AH: Social Security benefits credit
    * AJ: Military retirement credit
    * AM: Earned income tax credit
    """

    value_type = float
    entity = TaxUnit
    label = "UT apportionable nonrefundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT
