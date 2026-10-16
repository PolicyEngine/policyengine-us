from policyengine_us.model_api import *


class mt_dependent_gross_income(Variable):
    value_type = float
    entity = Person
    label = "Montana gross income of a dependent for the dependent exemption"
    unit = USD
    documentation = """
    Montana gross income (MCA 15-30-2101(10)) is federal gross income under
    IRC 61, excluding unemployment compensation. This starts from the federal
    dependent_gross_income, which counts gains but not losses and only the
    IRC 86 taxable part of Social Security (figured on the dependent's own
    modified AGI, which includes unemployment compensation), and removes the
    dependent's unemployment compensation.
    """
    definition_period = YEAR
    reference = (
        # MCA 15-30-2101(10) (2021): gross income is IRC 61 gross income
        # excluding unemployment compensation.
        "http://web.archive.org/web/20220127192023/http://leg.mt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0010/0150-0300-0210-0010.html",
        # MCA 15-30-2114(5)(a) (2021): the dependent gross income test.
        "http://web.archive.org/web/20220818141612/https://leg.mt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0140/0150-0300-0210-0140.html",
        # ARM 42.15.403 restates the test; its subsection numbers are not
        # verified because the rule text was not machine-readable.
        "https://rules.mt.gov/gateway/ruleno.asp?RN=42.15.403",
        # 2022 Form 2 instructions: "federal gross income, excluding
        # unemployment compensation".
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=7",
    )
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        federal_gross_income = person("dependent_gross_income", period)
        # dependent_gross_income counts a dependent's unemployment
        # compensation in full whenever it is a federal gross income source.
        sources = parameters(period).gov.irs.gross_income.sources
        unemployment_compensation_counted = (
            "taxable_unemployment_compensation" in sources
        ) * max_(0, person("total_unemployment_compensation", period))
        # dependent_gross_income is zero for the head and spouse.
        is_dependent = ~person("is_tax_unit_head_or_spouse", period)
        return federal_gross_income - is_dependent * unemployment_compensation_counted
