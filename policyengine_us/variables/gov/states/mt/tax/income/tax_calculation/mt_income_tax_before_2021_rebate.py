from policyengine_us.model_api import *


class mt_income_tax_before_2021_rebate(Variable):
    value_type = float
    entity = Person
    label = "Montana income tax before refundable credits and the 2021 rebate"
    unit = USD
    definition_period = YEAR
    reference = (
        # MCA 15-30-2191(1)(a), (2) and (6): rebate capped at the 2021 liability
        # as properly reported on Form 2 line 20
        "https://web.archive.org/web/20250210203531/https://archive.legmt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0910/0150-0300-0210-0910.html",
        # Montana HB 192 (Ch. 44, L. 2023), enrolled bill, Sec. 2(1)(a) and (2)
        "https://web.archive.org/web/20230626082025/https://leg.mt.gov/bills/2023/billpdf/HB0192.pdf#page=1",
        # 2021 Montana Form 2, lines 18-20 and Column B (filing status 2a)
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2021_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=1",
        # Montana Department of Revenue rebate report, May 2024, pp. 10-11:
        # couples filing separately (status 2a) treated as separate individuals
        "https://archive.legmt.gov/content/Committees/Interim/2023-2024/Revenue/Meetings/May-2024/5.1-DOR-rebate-report.pdf#page=13",
    )
    defined_for = StateCode.MT

    # Each column's share of 2021 Form 2 line 20 (tax after nonrefundable
    # credits: line 18 less line 19) without the 2021 income tax rebate. It is
    # the base for the rebate's liability cap (MCA 15-30-2191(2)). The Montana
    # Department of Revenue treated married couples who filed separately
    # (status 2a) as separate individuals, so a column filing separately is
    # capped at its own line 20. A joint return splits its line 20 evenly
    # across the head and spouse columns. The separate-vs-joint choice here is
    # made on rebate-free liabilities: the rebate is a refundable payment
    # subtracted equally on both paths, so it cannot move the election, and
    # reading it here would create a cycle (taxsim #1189).
    def formula(person, period, parameters):
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        capital_gain_credit = person("mt_capital_gain_credit", period)
        # Separately-filed column: own line 20 (before the rebate).
        indiv_before_credits = person(
            "mt_income_tax_before_non_refundable_credits_indiv", period
        )
        indiv_line_20 = max_(indiv_before_credits - capital_gain_credit, 0)
        # Jointly-filed return: the return's line 20, shared evenly across the
        # head and spouse columns claiming the rebate.
        joint_before_credits = person.tax_unit(
            "mt_income_tax_before_non_refundable_credits_joint", period
        )
        joint_capital_gain_credit = person.tax_unit.sum(capital_gain_credit)
        joint_line_20 = max_(joint_before_credits - joint_capital_gain_credit, 0)
        claimants = person.tax_unit.sum(head_or_spouse)
        joint_share = where(claimants > 0, joint_line_20 / claimants, 0)
        # The couple files separately when doing so lowers the rebate-free
        # liability, mirroring mt_files_separately without depending on the
        # rebate (which would create a cycle).
        indiv_line_20_unit = person.tax_unit.sum(indiv_line_20)
        p = parameters(period).gov.states.mt.tax.income
        separate_allowed = p.married_filing_separately_on_same_return_allowed
        cheaper_separately = indiv_line_20_unit < joint_line_20
        files_separately = separate_allowed & cheaper_separately
        return where(files_separately, indiv_line_20, joint_share)
