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

    # The rebate is based on 2021 income tax liability but was paid in 2023. It
    # is booked to tax year 2021 as a Montana refundable payment (see
    # mt_refundable_credits), so it reduces Montana tax and raises household
    # net income without entering the separate-vs-joint election.
    #
    # The cap applies once per return (MCA 15-30-2191(1)(b)), so a joint return
    # splits its $2,500 across the head and spouse columns ($1,250 each) rather
    # than paying $2,500 per spouse. MCA 15-30-2191(2) limits the rebate to the
    # 2021 liability on Form 2 line 20, before the rebate itself. The Montana
    # Department of Revenue treated married couples who filed separately
    # (status 2a) as separate individuals, so each column receives the lesser
    # of $1,250 and its own line 20; a joint column receives the lesser of
    # $1,250 and half the joint line 20 (mt_income_tax_before_2021_rebate).
    # This fixes the overstatement when line 20 was below the cap (taxsim
    # #1189).
    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.credits.rebate
        filing_status = person.tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        per_person_cap = where(
            filing_status == statuses.JOINT,
            p.amount["SEPARATE"],
            p.amount[filing_status],
        )
        line_20 = person("mt_income_tax_before_2021_rebate", period)
        return head_or_spouse * min_(per_person_cap, line_20)
