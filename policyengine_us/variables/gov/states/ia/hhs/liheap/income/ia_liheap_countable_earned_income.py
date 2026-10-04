from policyengine_us.model_api import *


class ia_liheap_countable_earned_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Iowa LIHEAP countable earned income"
    documentation = (
        "Gross earned income of household members aged 18 and over: wages, "
        "military basic pay, self-employment and farm income. Appendix C counts "
        "self-employment on gross receipts ('The LIHEAP program does NOT deduct "
        "business expenses'); the model's net business and farm inputs are each "
        "floored at zero so a loss does not offset other income, and they "
        "understate Iowa's gross basis when expenses exist. All income of "
        "members under 18 is excluded."
    )
    reference = (
        # Section 6.00 (page 24), Section 6.20 (page 26), Appendix C Employment
        # Income (page 97), Farm Income (page 98), Income Earned by HH Members
        # under the age of 18 (page 102), Military Pay (page 108) and
        # Self-Employment Income (page 113).
        "https://hhs.iowa.gov/media/17262/download?inline#page=113",
        # Sections 1.8-1.9, pages 5-6.
        "https://liheapch.acf.gov/docs/2026/state-plans/IA_Plan_2026.pdf#page=5",
    )
    defined_for = StateCode.IA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ia.hhs.liheap.income
        earned = 0
        for source in p.sources.earned:
            # Appendix C, Self-Employment Income: gross receipts are counted
            # and business expenses are not deducted, so a reported loss
            # cannot reduce other income.
            earned = earned + max_(person(source, period), 0)
        age = person("age", period)
        # Section 6.20 counts "the gross income of all household members aged
        # 18 and over". Section 6.00 (page 24) says income of individuals under
        # 18 is exempt "unless working full-time or the individual is
        # emancipated and applying as head of household", but Appendix C (page
        # 102) says earnings of under-18 members who "work full-time" are "NOT
        # included as income" and the FFY2026 plan leaves "Earned income of a
        # child under the age of 18" unchecked. The model follows Section 6.20,
        # Appendix C and the plan: all under-18 income is excluded (user
        # decision of 2026-10-04); the Section 6.00 wording is a recorded
        # conflict.
        return where(age >= p.countable_min_age, earned, 0)
