from policyengine_us.model_api import *


class ut_nonapportionable_nonrefundable_credits(Variable):
    """
    Line 26 on Utah 2022 Individual Income Tax return form TC-40. These
    credits include the following categories and are listed at
    https://incometax.utah.gov/credits with their accompanying codes.
    * 01: At-home parent credit
    * 02: Qualified sheltered workshop cash contribution credit
    * 06: Historic preservation credit
    * 08: Low-income housing credit
    * 12: Credit for increasing research activities in Utah
    * 13: Carryforward of credit for machinery and equipment used to conduct research
    * 17: Credit for income tax paid to another state
    * 19: Live organ donation expenses credit
    * 21: Renewable residential energy systems credit
    * 25: Combat related death credit
    * 27: Veteran employment credit
    * 28: Employing persons who are homeless credit
    * 63: Achieving a Better Life Experience (ABLE) program credit
    * AA: Military survivor benefits credit
    * AG: Special Needs Opportunity Scholarship Program credit
    * AP: Pass-through entity taxpayer income tax credit
    """

    value_type = float
    entity = TaxUnit
    label = "UT nonapportionable nonrefundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT
