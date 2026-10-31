from policyengine_us.model_api import *


class nv_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Nevada LIHEAP countable income"
    documentation = (
        "Annual gross income used for the income eligibility test. TANF and "
        "the earnings of school-attending children are excluded here and "
        "counted in nv_liheap_fac_income."
    )
    defined_for = StateCode.NV
    reference = (
        # PDF pages 43-44, 46-48, 57, 60
        "https://dss.nv.gov/uploadedFiles/dwssnvgov/content/Energy/FY%202026%20EAP%20Manual%2008.2025%20ADA.pdf#page=43",
        # PDF pages 43-44, 46-48, 57, 60
        "https://www.dss.nv.gov/contentassets/b3bcdb93ea2d4b3f8dc252451a34cbe4/2027-eap-state-manual--08.25.26-1.pdf#page=43",
        # PDF pages 5-6
        "https://liheapch.acf.gov/docs/2026/state-plans/NV_Plan_2026.pdf#page=5",
        # PDF pages 5-6
        "https://www.dss.nv.gov/contentassets/b3bcdb93ea2d4b3f8dc252451a34cbe4/fy-2027-low-income-home-energy-assistance-program-liheap-state-plan.pdf#page=5",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nv.dwss.liheap.income
        person = spm_unit.members
        # The earnings of a member under 18 in school are excluded here and
        # counted toward the Fixed Annual Credit.
        earned = person("nv_liheap_earned_income", period) - person(
            "nv_liheap_child_earned_income", period
        )
        # Each unearned source is floored at zero.
        unearned = 0
        for source in p.sources.unearned:
            unearned = unearned + max_(person(source, period, options=[ADD]), 0)
        # The only deductions from unearned income are the Medicare premiums
        # taken from a Social Security check; only the Part B premium has an
        # input.
        social_security = max_(
            person("social_security", period)
            - person("medicare_part_b_premium", period),
            0,
        )
        # Members excluded from household size keep their income, subject to
        # the same children's earned income exclusion as other members.
        return spm_unit.sum(earned + unearned + social_security)
