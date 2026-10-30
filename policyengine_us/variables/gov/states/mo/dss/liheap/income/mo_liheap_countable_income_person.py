from policyengine_us.model_api import *


class mo_liheap_countable_income_person(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Missouri LIHEAP countable income per person"
    documentation = "Gross income Missouri counts for a household member, including a member left out of the household size as a non-citizen: earned income after the earned income deduction plus unearned income, less the SMI (Medicare Part B) premium of a member who receives Social Security or Railroad Retirement benefits, floored at zero. Each earned and unearned source is floored at zero, so business, farm and rental losses do not offset other income. Members under 18 have their earned income and their non-Social Security disability payments excluded; their Social Security and SSI count. Not modeled: Medicare Part D premiums. Annual income stands in for twelve times the income of the month before application."
    reference = (
        # PDF pages 5-7
        "https://liheapch.acf.gov/docs/2026/state-plans/MO_Plan_2026.pdf#page=5",
        # PDF pages 4-5
        "https://dssmanuals.mo.gov/wp-content/uploads/2022/02/liheap-application.pdf#page=4",
        # DSS draft FFY2027 plan (report status "Saved -- with Errors").
        # PDF pages 5-7
        "https://dss.mo.gov/sites/mydss/files/media/pdf/2026/08/liheap-active-ffy2027.pdf#page=5",
        # PDF pages 32, 34, 36, 38, 42-43
        "https://dss.mo.gov/sites/mydss/files/media/pdf/2025/10/liheap-policy-procedure-manual.pdf#page=32",
    )
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mo.dss.liheap.income
        earned = 0
        for source in p.earned_sources:
            earned = earned + max_(person(source, period), 0)
        countable_earned = earned * (1 - p.earned_income_deduction_rate)
        # The 2025 manual (Earnings of Children) leaves out the earned income
        # and the disability income of members under 18 but counts their SSA
        # income, read here as Social Security and SSI.
        adult_income = countable_earned + add(person, period, p.adult_unearned_sources)
        adult = person("age", period) >= p.adult_age
        # Each unearned source is floored at zero, so a rental loss does not
        # offset other income; add() also sums monthly sources such as SSI.
        unearned = 0
        for source in p.unearned_sources:
            unearned = unearned + max_(add(person, period, [source]), 0)
        social_security = person("social_security", period)
        # The 2025 manual (page 36) deducts the SMI premium for members who
        # receive Social Security or Railroad Retirement benefits and pay it.
        receives_ss_or_rrb = (social_security > 0) | (
            person("railroad_benefits", period) > 0
        )
        smi_premium = where(
            receives_ss_or_rrb, person("medicare_part_b_premium", period), 0
        )
        gross = unearned + social_security + where(adult, adult_income, 0)
        return max_(gross - smi_premium, 0)
