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
        "https://web.archive.org/web/20230626082025/https://leg.mt.gov/bills/2023/billpdf/HB0192.pdf#page=2",
        # Montana HB 816 (2023), Sec. 4 (MCA 15-30-2191(6)): "properly reported"
        # covers the timely 2021 return or an amended return filed on or before
        # May 1, 2023
        "https://web.archive.org/web/20230607192457/https://leg.mt.gov/bills/2023/billpdf/HB0816.pdf#page=5",
        # 2021 Montana Form 2, lines 18-20 and Column B (filing status 2a)
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2021_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=1",
        # 2021 Montana Form 2 instructions, Filing Status: a spouse filing
        # separately on the same form (status 2a) files a separate return
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2021_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=10",
        # Montana Department of Revenue rebate report, May 2024, printed p. 7:
        # married couples amended 2021 returns to maximize the rebate
        "https://archive.legmt.gov/content/Committees/Interim/2023-2024/Revenue/Meetings/May-2024/5.1-DOR-rebate-report.pdf#page=9",
        # Montana Department of Revenue rebate report, May 2024, printed p. 11:
        # couples filing separately (status 2a) treated as separate individuals
        "https://archive.legmt.gov/content/Committees/Interim/2023-2024/Revenue/Meetings/May-2024/5.1-DOR-rebate-report.pdf#page=13",
    )
    defined_for = StateCode.MT

    # Each column's share of 2021 Form 2 line 20 (line 18 tax less all line 19
    # nonrefundable credits) without the 2021 income tax rebate. It is the base
    # for the rebate's liability cap (MCA 15-30-2191(2)). The Montana
    # Department of Revenue treated married couples who filed separately
    # (status 2a) as separate individuals, so a column filing separately is
    # capped at its own line 20. A joint return splits its line 20 evenly
    # across the head and spouse columns. Dependents' columns are zero.
    #
    # Models the 2021 return as originally filed (the MCA 15-30-2191(6)
    # default). Couples who amended from status 2a to joint by May 1, 2023
    # (HB 816 Sec. 4) could receive up to $2,500; not modeled. The
    # separate-vs-joint election excludes the rebate by assumption, so it is
    # made on rebate-free liabilities here. This variable cannot read
    # mt_files_separately, which depends on the rebate through
    # mt_refundable_credits, so it repeats that election.
    #
    # Line 20 comes from mt_income_tax_before_refundable_credits_indiv and
    # _joint, which subtract gov.states.mt.tax.income.credits.non_refundable.
    # The rebate must never go back into that list: it would become an input
    # to its own cap base and create a cycle.
    def formula(person, period, parameters):
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # Separately filed column: its own line 20, already floored at zero
        # and limited to the head and spouse.
        indiv = person("mt_income_tax_before_refundable_credits_indiv", period)
        # Jointly filed return: the return's line 20, shared evenly across the
        # head and spouse columns.
        joint = person.tax_unit("mt_income_tax_before_refundable_credits_joint", period)
        claimants = person.tax_unit.sum(head_or_spouse)
        joint_share = np.divide(
            joint,
            claimants,
            out=np.zeros_like(joint),
            where=claimants > 0,
        )
        # The couple files separately when doing so lowers the rebate-free
        # line 20, mirroring mt_income_tax_before_refundable_credits_unit.
        p = parameters(period).gov.states.mt.tax.income
        separate_allowed = p.married_filing_separately_on_same_return_allowed
        cheaper_separately = person.tax_unit.sum(indiv) < joint
        files_separately = separate_allowed & cheaper_separately
        return head_or_spouse * where(files_separately, indiv, joint_share)
