from policyengine_us.model_api import *


class mt_dependent_exemptions_person(Variable):
    value_type = int
    entity = Person
    label = "Montana dependent exemption for each dependent"
    unit = USD
    definition_period = YEAR
    reference = (
        # MCA 15-30-2114(5)(a) (2021): the dependent exemption.
        "http://web.archive.org/web/20220818141612/https://leg.mt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0140/0150-0300-0210-0140.html",
        # MCA 15-30-2101(10) (2021): the definition of gross income.
        "http://web.archive.org/web/20220127192023/http://leg.mt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0010/0150-0300-0210-0010.html",
        "https://regulations.justia.com/states/montana/department-42/chapter-42-15/subchapter-42-15-4/rule-42-15-403/",
        # Form 2 instructions, dependents: 2021 ($2,580), 2022 ($2,710) and
        # 2023 ($2,960).
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2021_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=13",
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=14",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=16",
    )
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.exemptions

        if p.applies:
            # A qualifying child under IRC 152(c) is a dependent regardless of
            # income. Any other dependent counts only if their gross income
            # does not exceed the exemption amount (Form 2 instructions: a
            # dependent is an individual "who does not have gross income of
            # more than" the exemption amount "unless the dependent is a
            # 'qualifying child' according to the federal rules").
            dependent = person("is_tax_unit_dependent", period)
            # A permanently and totally disabled child is a qualifying child
            # at any age (IRC 152(c)(3)(B)), as in
            # is_qualifying_relative_dependent.
            qualifying_child = person("is_qualifying_child_dependent", period) | (
                dependent & person("is_permanently_and_totally_disabled", period)
            )
            # MCA 15-30-2114(5)(a) tests the dependent's own gross income as
            # defined in MCA 15-30-2101(10): federal gross income excluding
            # unemployment compensation, with only taxable Social Security.
            gross_income = person("mt_dependent_gross_income", period)
            other_dependent = dependent & ~qualifying_child & (gross_income <= p.amount)
            # Disabled children get an additional exemption.
            disabled = person("is_disabled", period)

            eligible_dependent = qualifying_child * (1 + disabled) + other_dependent
            return eligible_dependent * p.amount

        return 0
