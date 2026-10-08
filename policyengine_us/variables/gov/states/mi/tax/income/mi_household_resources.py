from policyengine_us.model_api import *


class mi_household_resources(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan household resources"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MI
    reference = (
        "https://law.justia.com/codes/michigan/2022/chapter-206/"
        "statute-act-281-of-1967/division-281-1967-1/division-281-1967-1-9/"
        "section-206-508/",
        "https://www.legislature.mi.gov/Laws/MCL?objectName=mcl-206-508",
        # MCL 206.510(1): "Income", including premiums paid for the family.
        "https://www.legislature.mi.gov/Laws/MCL?objectName=mcl-206-510",
        "https://web.archive.org/web/20250202150154/https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2024/BOOK_MI-1040CR-7.pdf",
        # 2025 MI-1040 book: "Total Household Resources" (pages 26 and 27,
        # with what they do not include) and MI-1040CR lines 14 to 17 (page
        # 31) and 18 to 31 (pages 32 and 33).
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/"
        "Forms/IIT/TY2025/MI-1040-Book.pdf#page=26",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/"
        "Forms/IIT/TY2025/MI-1040-Book.pdf#page=27",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/"
        "Forms/IIT/TY2025/MI-1040-Book.pdf#page=31",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/"
        "Forms/IIT/TY2025/MI-1040-Book.pdf#page=32",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/"
        "Forms/IIT/TY2025/MI-1040-Book.pdf#page=33",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mi.tax.income
        # MCL 206.508(4) increases income by "(a) Any net business loss after
        # netting all business income and loss" and "(b) Any net rental or
        # royalty loss". The MI-1040CR nets each group and floors the total
        # at zero, so a loss offsets income only within its own line.
        # Line 16: U.S. Schedule C, Form 4797 Part II, Schedule E Parts II
        # and III, and Schedule F. "If the total is negative enter 0."
        business_sources = {
            "total_self_employment_income",
            "other_net_gain",
            "partnership_s_corp_income",
            "estate_income",
            "farm_operations_income",
        }
        # Line 17: U.S. Schedule E Parts I, IV and V (rents, royalties, REMIC
        # income, which has no input here, and farm rental income). "If the
        # total is negative enter 0."
        rental_sources = {
            "rental_income",
            "farm_rent_income",
        }
        # MCL 206.510(1): income does not include "(a) The first $300.00 of
        # gifts in cash or kind from nongovernmental sources" or "(b) The
        # first $300.00 received from awards, prizes, lottery, bingo, or
        # other gambling winnings". The MI-1040CR enters gambling winnings
        # "over $300" on line 20 and "the value over $300 in gifts" on line
        # 24 (2025 MI-1040 book, page 32), one amount for the claimant and
        # spouse, so the exclusion applies once to their total.
        winnings_sources = {"gambling_winnings"}
        gift_sources = {"financial_assistance"}

        # MCL 206.508(3): "'Household' means a claimant and spouse", and
        # (4) counts "all income received by all persons of a household".
        # The MI-1040CR says "Include all taxable and nontaxable income you
        # and your spouse received" (2025 MI-1040 book, page 31). A
        # dependent's own income belongs on the dependent's return, so a
        # source is summed over the head and spouse only, as in
        # irs_gross_income. A tax-unit-level source (other_net_gain,
        # filer_loss_limited_net_capital_gains) already describes the
        # filer's return.
        # The sources in household_resources_all_members are amounts the
        # claimant receives for others in the household (lines 21, 22 and
        # 27), so they are summed over every member. So is a source defined
        # for a larger group than the tax unit, such as tanf for the SPM
        # unit: add gives the tax unit its members' shares.
        all_members = p.household_resources_all_members

        business_income = 0
        rental_income = 0
        winnings = 0
        gifts = 0
        other_income = 0
        for source in p.household_resources:
            entity = tax_unit.entity.get_variable(source).entity
            own_return = entity.is_person or entity.key == tax_unit.entity.key
            if source in all_members or not own_return:
                amount = add(tax_unit, period, [source])
            else:
                amount = tax_unit_non_dep_add(tax_unit, period, [source])
            if source in business_sources:
                business_income += amount
            elif source in rental_sources:
                rental_income += amount
            elif source in winnings_sources:
                winnings += amount
            elif source in gift_sources:
                gifts += amount
            else:
                other_income += amount
        total = (
            other_income
            + max_(business_income, 0)
            + max_(rental_income, 0)
            + max_(winnings - p.household_resources_gambling_exclusion, 0)
            + max_(gifts - p.household_resources_gift_exclusion, 0)
        )

        # Line 30: "total adjustments from your U.S. Form 1040, Schedule 1".
        # Business, rental and capital losses are income items (Schedule 1
        # Part I and Schedule D), not Part II adjustments. They are netted
        # and floored on lines 16, 17 and 19 above, so loss_ald, which holds
        # them, is left out.
        # The Schedule 1 is the claimant's own: a dependent's adjustments,
        # like the dependent's income, are on the dependent's return.
        # Person-level adjustments are summed over the head and spouse, and
        # tax-unit-level ones are the filer's own: the self-employment and
        # alimony deductions sum only the head and spouse. Amounts that are
        # the filer's even when recorded on a dependent are summed over every
        # member, as in above_the_line_deductions.
        ald = parameters(period).gov.irs.ald
        deductions = [
            deduction for deduction in ald.deductions if deduction != "loss_ald"
        ]
        adjustments = tax_unit_non_dep_add(
            tax_unit,
            period,
            deductions,
            include_dependents=ald.filer_amounts_recorded_on_dependents,
        )
        # Line 31: "insurance premiums you paid for yourself and your
        # family". MCL 206.510(1) lets a person deduct "the amount that
        # person paid in premiums ... for that insurance plan for the
        # person's family". A premium on any member's record is read as one
        # the claimant or spouse paid for the family's coverage.
        premiums = add(tax_unit, period, ["health_insurance_premiums"])
        # "Do not include any insurance premiums deducted on lines 21 or 30"
        # (2025 MI-1040 book, page 33). Line 30 includes the self-employed
        # health insurance deduction (Schedule 1 line 17), so those premiums
        # leave line 31 and each premium dollar is subtracted once.
        # Line 21 nets out Medicare premiums withheld from Social Security or
        # railroad retirement benefits (MCL 206.510(1)(h)). Here line 21 has
        # gross benefits and line 31 the premiums, which subtracts them once
        # as well.
        premiums_on_line_30 = (
            tax_unit_non_dep_add(
                tax_unit, period, ["self_employed_health_insurance_ald"]
            )
            if "self_employed_health_insurance_ald" in deductions
            else 0
        )
        line_31 = max_(premiums - premiums_on_line_30, 0)
        return max_(0, total - adjustments - line_31)
