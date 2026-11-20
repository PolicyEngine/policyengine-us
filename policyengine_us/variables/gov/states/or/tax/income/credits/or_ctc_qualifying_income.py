from policyengine_us.model_api import *


class or_ctc_qualifying_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oregon Kids Credit qualifying income"
    unit = USD
    definition_period = YEAR
    documentation = (
        "The qualifying income limit of ORS 315.273(1)(c)(A) for a full-year "
        "resident: adjusted gross income as modified by Oregon additions and "
        "subtractions, plus the filer's losses to the extent they exceed "
        "$20,000 and, from 2025, foreign earned income excluded from adjusted "
        "gross income."
    )
    reference = (
        # 2023R1 House Bill 3235, Section 2(1)(c).
        "https://olis.oregonlegislature.gov/liz/2023R1/Downloads/MeasureDocument/HB3235/Enrolled#page=1",
        # Oregon Laws 2025, chapter 321, section 16 (PDF page 7) and section
        # 17(2) (PDF page 8).
        "https://www.oregonlegislature.gov/bills_laws/lawsstatutes/2025orlaw0321.pdf#page=7",
        # ORS 315.273, 2025 edition.
        "https://www.oregonlegislature.gov/bills_laws/ors/ors315.html",
        # 2025 Form OR-40 instructions, Oregon Kids Credit worksheet lines 1
        # to 4 (PDF page 23) and Part B, lines 11 to 13 (PDF page 24).
        "https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2025.pdf#page=23",
        "https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2025.pdf#page=24",
    )
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["or"].tax.income.credits.ctc.qualifying_income
        # ORS 315.273(1)(c)(A): "adjusted gross income ... as modified using
        # Oregon subtractions and additions" (worksheet line 1, Form OR-40
        # line 15). or_agi does not take the tip, overtime or vehicle interest
        # subtractions that worksheet line 2 adds back.
        or_agi = tax_unit("or_agi", period)
        # (1)(c)(A)(i): "Losses of the taxpayer, to the extent that those
        # losses exceed $20,000". Worksheet Part B, lines 11a to 11h: each
        # loss on these lines of the head's and spouse's federal return, as a
        # positive amount; a line that is not a loss counts as zero.
        loss_lines = (
            # 11a: Form 1040 line 7a, where a net capital loss is limited
            # under IRC 1211(b).
            ["filer_loss_limited_net_capital_gains"],
            # 11b: Schedule 1 line 3, business income or loss (Schedule C).
            ["total_self_employment_income"],
            # 11c: Schedule 1 line 4, other gains or losses (Form 4797).
            ["other_net_gain"],
            # 11d: Schedule 1 line 5, rental real estate, royalties,
            # partnerships, S corporations, estates and trusts (Schedule E,
            # including Form 4835 farm rents).
            [
                "rental_income",
                "farm_rent_income",
                "partnership_s_corp_income",
                "estate_income",
            ],
            # 11e: Schedule 1 line 6, farm income or loss (Schedule F).
            ["farm_operations_income"],
        )
        # Line 11f (the net operating loss deduction) and line 11g (losses on
        # Oregon subtraction codes 321 and 355 to 357) are not modeled.
        losses = 0
        for sources in loss_lines:
            line = tax_unit_non_dep_add(tax_unit, period, sources)
            losses = losses + max_(0, -line)
        excess_losses = max_(0, losses - p.loss_threshold)
        # (1)(c)(A)(ii), from 2025: excluded foreign earned income (worksheet
        # line 12, Schedule 1 line 8d).
        excluded_income = tax_unit_non_dep_add(tax_unit, period, p.additions)
        return or_agi + excess_losses + excluded_income
