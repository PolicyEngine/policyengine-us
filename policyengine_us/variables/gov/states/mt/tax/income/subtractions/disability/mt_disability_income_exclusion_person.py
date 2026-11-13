from policyengine_us.model_api import *


class mt_disability_income_exclusion_person(Variable):
    value_type = float
    entity = Person
    label = "Montana disability income exclusion for each person"
    documentation = (
        "Taxable disability benefits of a person eligible for the exclusion, up "
        "to the annual cap. Former MCA 15-30-2110(10) allowed up to $100 a "
        "week of benefits and reduced the exclusion by adjusted gross income "
        "above $15,000 (a married couple's combined income). The model "
        "applies the annual cap, 52 weeks at $100, without counting weeks of "
        "benefits, and does not apply the $15,000 reduction. Repealed from "
        "2024."
    )
    defined_for = "mt_disability_income_exclusion_eligible_person"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=31",
        # Former MCA 15-30-2110(10) (2021 edition): "up to $100 a week"; "If
        # the adjusted gross income before this exclusion exceeds $15,000,
        # the excess reduces the exclusion by an equal amount."
        "https://mca.legmt.gov/bills/2022/mca/title_0150/chapter_0300/part_0210/section_0100/0150-0300-0210-0100.html",
        # 2021 Mont. Laws ch. 503 (SB 399): section 65 repeals 15-30-2110,
        # MCA, which held the exclusion; section 70(1) applies the repeal to
        # tax years beginning after December 31, 2023.
        # PDF pages 68, 70
        "https://archive.legmt.gov/content/Publications/sales/2021SessionLaws_V3_ERRATA-VERSION.pdf#page=68",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.subtractions.disability_income
        # Not modelled: the weekly limit for fewer than 52 weeks of benefits
        # and the reduction above $15,000 of adjusted gross income (former
        # MCA 15-30-2110(10); tracked in rulespec-us#1741).
        exclusion = min_(p.cap, person("taxable_disability_benefits", period))
        # Repealed from 2024 (2021 Mont. Laws ch. 503, sections 65 and 70(1)),
        # even for a person whose eligibility is supplied as an input.
        return p.in_effect * exclusion
