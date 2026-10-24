from policyengine_us.model_api import *


class mt_disability_income_exclusion_person(Variable):
    value_type = float
    entity = Person
    label = "Montana disability income exclusion for each person"
    defined_for = "mt_disability_income_exclusion_eligible_person"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=31",
        # 2021 Mont. Laws ch. 503 (SB 399): section 65 repeals 15-30-2110,
        # MCA, which held the exclusion; section 70(1) applies the repeal to
        # tax years beginning after December 31, 2023.
        # PDF pages 68, 70
        "https://archive.legmt.gov/content/Publications/sales/2021SessionLaws_V3_ERRATA-VERSION.pdf#page=68",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.subtractions.disability_income
        return min_(p.cap, person("taxable_disability_benefits", period))

    def formula_2024(person, period, parameters):
        # Repealed from 2024 (2021 Mont. Laws ch. 503, sections 65 and 70(1)),
        # even for a person whose eligibility is supplied as an input.
        return 0
