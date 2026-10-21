from policyengine_us.model_api import *


class in_disability_retirement_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana disability retirement deduction"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Schedule 2 code 602 (Schedule IT-2440), for people who retired on "
        "disability and were permanently and totally disabled when they "
        "retired. There is no age limit. The weekly $100 limit is applied as "
        "an annual cap."
    )
    reference = (
        "https://law.justia.com/codes/indiana/title-6/article-3/chapter-2/section-6-3-2-9/",
        # PDF pages 1-2
        "https://www.in.gov/dor/files/reference/ib70.pdf#page=1",
    )
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        p = (
            parameters(period)
            .gov.states["in"]
            .tax.income.deductions.disability_retirement
        )
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        disability_pay = person("permanent_disability_retirement_pay", period)
        # Steps 1-2: the individual's disability pay, at most $100 a week.
        capped_pay = min_(disability_pay, p.cap)
        # Steps 3-4: less federal AGI above $15,000 ($7,500 married filing
        # separately), for each individual.
        filing_status = tax_unit("filing_status", period)
        agi = tax_unit("adjusted_gross_income", period)
        reduction = max_(0, agi - p.reduction_threshold[filing_status])
        deduction = max_(0, capped_pay - person.tax_unit.project(reduction))
        return tax_unit.sum(head_or_spouse * deduction)
