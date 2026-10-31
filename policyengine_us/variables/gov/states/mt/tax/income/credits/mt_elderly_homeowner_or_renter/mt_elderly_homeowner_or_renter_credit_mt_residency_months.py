from policyengine_us.model_api import *


class mt_elderly_homeowner_or_renter_credit_mt_residency_months(Variable):
    value_type = int
    entity = Person
    label = (
        "Months of Montana residence, for the Montana elderly homeowner/renter credit"
    )
    documentation = (
        "Months of the year, from 0 to 12, this person resided in Montana. "
        "Defaults to 12 for members of a Montana household, whose state the "
        "model treats as their residence for the whole year."
    )
    unit = "month"
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = (
        # MCA 15-30-2338(1)(b): resided in Montana "for at least 9 months"
        "https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0230/section_0380/0150-0300-0230-0380.html",
        "https://mca.legmt.gov/bills/2009/mca/15/30/15-30-2338.htm",
        # 2025 instructions: the claimant attests "You lived in Montana for at
        # least nine months during the tax year"
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2025_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=44",
    )

    def formula(person, period, parameters):
        return MONTHS_IN_YEAR
