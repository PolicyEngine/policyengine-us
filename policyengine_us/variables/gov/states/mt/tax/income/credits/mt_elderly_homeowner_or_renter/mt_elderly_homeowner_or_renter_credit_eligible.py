from policyengine_us.model_api import *


class mt_elderly_homeowner_or_renter_credit_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Montana Elderly Homeowner/Renter Credit"
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = (
        # MCA 15-30-2338(1)(a)-(c): age 62, 9 months of residence and 6 months
        # of occupancy as an owner, renter, or lessee
        "https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0230/section_0380/0150-0300-0230-0380.html",
        "https://mca.legmt.gov/bills/2009/mca/15/30/15-30-2338.htm",
        # 2025 instructions: the tests the claimant attests to, and "If you are
        # married filing jointly and both spouses own or rent the residence,
        # only one of you must meet the age requirement"
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2025_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=44",
    )

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.tax.income.credits.elderly_homeowner_or_renter
        # Section 15-30-2338(1) sets the tests for "an individual", so one head
        # or spouse must meet all of them. Another member's property tax,
        # which ARM 42.4.302(2)(b) lets an eligible claimant use as rent,
        # cannot establish the occupancy test.
        age_eligible = person("age", period) >= p.age_threshold
        residency_months = person(
            "mt_elderly_homeowner_or_renter_credit_mt_residency_months", period
        )
        occupancy_months = person(
            "mt_elderly_homeowner_or_renter_credit_qualifying_occupancy_months",
            period,
        )
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        qualifies = (
            head_or_spouse
            & age_eligible
            & (residency_months >= p.minimum_residency_months)
            & (occupancy_months >= p.minimum_occupancy_months)
        )
        # Every member of the return shares the result, so the credit stays
        # on the head when the qualifying claimant is the spouse.
        return person.tax_unit.any(qualifies)
