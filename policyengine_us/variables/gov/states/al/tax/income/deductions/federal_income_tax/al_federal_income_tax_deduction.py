from policyengine_us.model_api import *
from policyengine_us.tools.pinned_tbs import get_2020_irc_tbs


class al_federal_income_tax_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama federal income tax deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        # 2021 Alabama Form 40 booklet, Federal Income Tax Deduction Worksheet
        "https://www.revenue.alabama.gov/wp-content/uploads/2022/06/21f40abk.pdf#page=20",
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40abk.pdf#page=20",
    )
    defined_for = StateCode.AL

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.al.tax.income.deductions.federal_tax
        # `income_tax_before_refundable_credits` is the federal income tax after
        # non-refundable credits plus the net investment income tax, i.e. Part I
        # line 3 (2021 Form 1040 line 22 plus Form 8960 net investment income
        # tax) of the worksheet.
        federal_tax = tax_unit("income_tax_before_refundable_credits", period)

        # Part I (worksheet lines 1-6): subtract the actual refundable federal
        # credits (EITC, refundable CTC/ACTC, American Opportunity Credit).
        part_i = max_(federal_tax - add(tax_unit, period, p.credits), 0)

        # Part II (Act 2022-37) applies only to tax year 2021, the one year the
        # federal CTC/CDCC/EITC were expanded and made refundable by ARPA. The
        # 2022+ Alabama worksheets are Part I only, and the provision did not
        # exist before 2021, so in every other year the deduction is Part I.
        # (Restricting the 2020 recompute to 2021 also avoids cloning the whole
        # simulation in the current-year microsimulation.)
        if period.start.year != 2021:
            return part_i

        # Part II (worksheet lines 1-14, per Act 2022-37): recompute the CTC,
        # CDCC, and EITC as if the IRC in effect on 2020-12-31 applied, then
        # take the greater deduction. ARPA (2021) expanded and made these
        # credits refundable, which otherwise shrinks the deduction; the
        # recompute lets Alabama filers keep the pre-ARPA (larger) deduction.
        ctc = tax_unit("ctc", period)
        refundable_ctc = tax_unit("refundable_ctc", period)
        # Non-refundable CTC (line 1b) and CDCC (line 1c) that `federal_tax`
        # already netted out, added back (lines 1b/1c) so they can be replaced
        # by the recomputed 2020 amounts below. In 2021 the CDCC is fully
        # refundable, so its non-refundable portion is zero.
        actual_non_refundable_ctc = ctc - refundable_ctc
        cdcc_is_refundable = "cdcc" in parameters(period).gov.irs.credits.refundable
        actual_non_refundable_cdcc = tax_unit("cdcc", period) * (not cdcc_is_refundable)

        simulation = tax_unit.simulation
        branch = simulation.get_branch("al_2020_irc")
        branch.tax_benefit_system = get_2020_irc_tbs(simulation.tax_benefit_system)
        for variable in branch.tax_benefit_system.variables:
            if any(key in variable for key in ("ctc", "cdcc", "eitc")):
                branch.delete_arrays(variable)
        recomputed_ctc = branch.tax_unit("ctc", period)
        recomputed_refundable_ctc = branch.tax_unit("refundable_ctc", period)
        # Under the 2020 IRC the CDCC is non-refundable (limited by tax), so the
        # branch's `cdcc` is the recomputed non-refundable amount (line 4).
        recomputed_non_refundable_ctc = recomputed_ctc - recomputed_refundable_ctc
        recomputed_cdcc = branch.tax_unit("cdcc", period)
        recomputed_eitc = branch.tax_unit("eitc", period)

        # Worksheet line 11 (2021 Form 1040 line 29) is the REFUNDABLE portion of
        # the American Opportunity Credit (Form 8863 line 8). The non-refundable
        # portion already reduced `federal_tax`, so subtracting the total would
        # double-count it.
        refundable_american_opportunity_credit = tax_unit(
            "refundable_american_opportunity_credit", period
        )

        # `federal_tax` (Part I line 3) includes the net investment income tax,
        # which the worksheet only adds on Part II line 7 (after the line-6
        # floor). Split it out so nonrefundable credits cannot erode the NIIT.
        niit = tax_unit("net_investment_income_tax", period)
        regular_tax_basis = federal_tax - niit

        # Lines 1e-6: recompute regular tax net of the 2020-rule nonrefundable
        # CTC/CDCC (after adding back the actual nonrefundable amounts that
        # `federal_tax` already netted out), then floor at zero on line 6.
        line_6 = max_(
            regular_tax_basis
            + actual_non_refundable_ctc
            + actual_non_refundable_cdcc
            - recomputed_non_refundable_ctc
            - recomputed_cdcc,
            0,
        )
        # Line 7 adds NIIT back; lines 13-14 subtract the refundable credits and
        # apply the final zero floor.
        part_ii = max_(
            line_6
            + niit
            - recomputed_eitc
            - recomputed_refundable_ctc
            - refundable_american_opportunity_credit,
            0,
        )

        return max_(part_i, part_ii)
