from policyengine_us.model_api import *


class mt_income_tax_rebate(Variable):
    value_type = float
    entity = Person
    label = "Montana 2021 income tax rebate"
    unit = USD
    definition_period = YEAR
    reference = "https://archive.legmt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0910/0150-0300-0210-0910.html"
    defined_for = StateCode.MT

    # The rebate is based on 2021 income tax liability, but provided in 2023.
    # It applies once per return (MCA 15-30-2191(1)), so joint filers split
    # the per-return cap across each spouse's column ($1,250 each) to avoid
    # double-counting when the person-level non-refundable credits are pooled.
    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.credits.rebate
        filing_status = person.tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        per_person_amount = where(
            filing_status == statuses.JOINT,
            p.amount["SEPARATE"],
            p.amount[filing_status],
        )
        return head_or_spouse * per_person_amount
