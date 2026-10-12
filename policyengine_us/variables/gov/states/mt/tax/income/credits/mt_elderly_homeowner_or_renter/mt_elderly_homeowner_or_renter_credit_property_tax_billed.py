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

    def formula(tax_unit, period, parameters):
        # Schedule 2EC line 23 is "the property tax you were billed". A joint
        # return makes one claim, so the claimant is the head and spouse.
        # When either is billed property tax, the home is in the claimant's
        # name and the tax unit's bills count here, including a dependent
        # co-owner's. When neither is, the home is in a name other than the
        # claimant's, a dependent's included, and its property tax "can
        # qualify as rent only" (ARM 42.4.302(2)(b)): line 23 is 0 and
        # mt_elderly_homeowner_or_renter_credit_gross_rent counts it.
        person = tax_unit.members
        property_tax = person("real_estate_taxes", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        claimant_billed = tax_unit.sum(property_tax * head_or_spouse) > 0
        return where(claimant_billed, tax_unit.sum(property_tax), 0)
