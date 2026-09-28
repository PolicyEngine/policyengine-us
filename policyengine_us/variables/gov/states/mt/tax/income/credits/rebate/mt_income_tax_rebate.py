from policyengine_us.model_api import *


class mt_income_tax_rebate(Variable):
    value_type = float
    entity = Person
    label = "Montana 2021 income tax rebate"
    unit = USD
    definition_period = YEAR
    reference = [
        # MCA 15-30-2191(1)(b)(i)-(ii) (rebate amounts) and (2) (line-20 cap)
        "https://web.archive.org/web/20250210203531/https://archive.legmt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0910/0150-0300-0210-0910.html",
        # Montana HB 192 (Ch. 44, L. 2023), enrolled bill, sec. 2
        "https://web.archive.org/web/20230626082025/https://leg.mt.gov/bills/2023/billpdf/HB0192.pdf",
        # Montana Department of Revenue, income tax and property tax rebate
        # report, May 2024, p. 8
        "https://archive.legmt.gov/content/Committees/Interim/2023-2024/Revenue/Meetings/May-2024/5.1-DOR-rebate-report.pdf#page=8",
    ]
    defined_for = StateCode.MT

    # The rebate is based on 2021 income tax liability, but provided in 2023.
    # It applies once per return (MCA 15-30-2191(1)), so joint filers split
    # the per-return cap across each spouse's column ($1,250 each) to avoid
    # double-counting when the person-level non-refundable credits are pooled.
    #
    # MCA 15-30-2191(2) caps the rebate at the 2021 liability reported on line
    # 20 of Form 2. That cap is not applied here: the ordered non-refundable
    # credit application already floors each path at zero, so the effective
    # rebate is line-20-capped per filing configuration. The guarding cases are
    # "Single filer below the cap" and "Rebate cannot drive liability below
    # zero" in the matching test file under
    # tests/policy/baseline/gov/states/mt/tax/income/credits/rebate/.
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
