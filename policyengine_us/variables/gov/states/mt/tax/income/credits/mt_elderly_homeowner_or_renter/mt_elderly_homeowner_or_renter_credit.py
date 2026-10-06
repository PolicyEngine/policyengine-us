from policyengine_us.model_api import *


class mt_elderly_homeowner_or_renter_credit(Variable):
    value_type = float
    entity = Person
    label = "Montana Elderly Homeowner/Renter Credit"
    unit = USD
    definition_period = YEAR
    defined_for = "mt_elderly_homeowner_or_renter_credit_eligible"
    reference = (
        "https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0230/section_0410/0150-0300-0230-0410.html",
        # 2024 Form 2, Schedule 2EC
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2/2024_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=10",
    )

    def formula(person, period, parameters):
        # Only one claimant per household is entitled to relief
        # (§ 15-30-2341(1)).
        credit = person(
            "mt_elderly_homeowner_or_renter_credit_pre_one_claimant", period
        )
        selected = person.tax_unit(
            "mt_elderly_homeowner_or_renter_credit_selected_claimant", period
        )
        return credit * selected
