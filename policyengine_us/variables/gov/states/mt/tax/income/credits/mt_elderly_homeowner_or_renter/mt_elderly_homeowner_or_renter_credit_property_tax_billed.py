from policyengine_us.model_api import *


class mt_elderly_homeowner_or_renter_credit_property_tax_billed(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana property tax billed for the elderly homeowner/renter credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = (
        # § 15-30-2337(10): property tax billed; § 15-30-2340(1): a claimant
        # who owns the homestead
        "https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0230/section_0370/0150-0300-0230-0370.html",
        "https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0230/section_0400/0150-0300-0230-0400.html",
        # ARM 42.4.302(2)(b): property in a name other than the claimant
        "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-42.4.302",
        # 2025 Schedule 2EC line 23: "the property tax you were billed"
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2/2025_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=10",
        # PDF pages 46-47: line 23, and property "in a name other than your
        # own"
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2025_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=46",
    )

    # Schedule 2EC line 23 is "the property tax you were billed". The
    # model counts the real_estate_taxes of everyone in the tax unit,
    # dependents included. real_estate_taxes is an expense amount, not a
    # record of whose name is on the title: the microdata mostly put a
    # household's bill on its reference person, who can be a tax unit
    # dependent. So it cannot show a home wholly in a dependent's name,
    # and a dependent's bill stays the claimant's.
    # When no one in the tax unit is billed, the home is treated as in
    # another household member's name, whose property tax "can qualify
    # as rent only" (ARM 42.4.302(2)(b)); see
    # mt_elderly_homeowner_or_renter_credit_gross_rent.
    adds = ["real_estate_taxes"]
