from policyengine_us.model_api import *


class mt_disability_income_exclusion_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Montana disability income exclusion eligible person"
    defined_for = StateCode.MT
    definition_period = YEAR
    reference = (
        "https://rules.mt.gov/gateway/RuleNo.asp?RN=42%2E15%2E217",
        # 2021 Mont. Laws ch. 503 (SB 399): section 65 repeals 15-30-2110,
        # MCA, which held the exclusion; section 70(1) applies the repeal to
        # tax years beginning after December 31, 2023.
        # PDF pages 68, 70
        "https://archive.legmt.gov/content/Publications/sales/2021SessionLaws_V3_ERRATA-VERSION.pdf#page=68",
        # 2024 Form 2 instructions, repealed deductions: "Partial retirement
        # disability deduction for taxpayers under age 65"
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2024_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=5",
    )

    def formula(person, period, parameters):
        # first select head and spouse with ages below the specific threshold, and
        # select those who are retired on total disability and disabled.
        p = parameters(period).gov.states.mt.tax.income.subtractions.disability_income
        age_eligible = person("age", period) < p.age_threshold
        is_retired_on_disability = person("retired_on_total_disability", period)
        eligible_retiree = age_eligible & is_retired_on_disability
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return eligible_retiree & head_or_spouse

    def formula_2024(person, period, parameters):
        # The exclusion is repealed for tax years beginning after December 31,
        # 2023 (2021 Mont. Laws ch. 503, sections 65 and 70(1)).
        return False
