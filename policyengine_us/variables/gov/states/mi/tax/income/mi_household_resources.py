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
        "https://web.archive.org/web/20250202150154/https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2024/BOOK_MI-1040CR-7.pdf",
        # 2025 MI-1040 book: "Total Household Resources" (page 26) and
        # MI-1040CR lines 16 and 17 (page 31), 19 and 30 (page 32).
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/"
        "Forms/IIT/TY2025/MI-1040-Book.pdf#page=26",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/"
        "Forms/IIT/TY2025/MI-1040-Book.pdf#page=31",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/"
        "Forms/IIT/TY2025/MI-1040-Book.pdf#page=32",
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

        # MCL 206.508(3): "'Household' means a claimant and spouse." A
        # dependent's business and rental items belong on the dependent's own
        # return, so they neither add to nor net against lines 16 and 17, as
        # loss_ald leaves them off this return. tax_unit_non_dep_add sums a
        # person-level source over the head and spouse and takes a
        # tax-unit-level one (other_net_gain) as is.
        business_income = 0
        rental_income = 0
        other_income = 0
        for source in p.household_resources:
            if source in business_sources:
                business_income += tax_unit_non_dep_add(tax_unit, period, [source])
            elif source in rental_sources:
                rental_income += tax_unit_non_dep_add(tax_unit, period, [source])
            else:
                other_income += add(tax_unit, period, [source])
        total = other_income + max_(business_income, 0) + max_(rental_income, 0)

        # Line 30: "Enter total adjustments from your U.S. Form 1040,
        # Schedule 1." These are the Schedule 1 Part II adjustments, counted
        # while the federal above-the-line list deducts them, so a reform that
        # drops one federally drops it here too. The rest of the federal list
        # is not on line 30:
        # - loss_ald holds business, rental and capital losses, which are
        #   income items netted and floored on lines 16, 17 and 19 above;
        # - us_bonds_for_higher_ed, qualified_adoption_assistance_expense,
        #   specified_possession_income and puerto_rico_income are income
        #   that IRC 135, 137, 931 and 933 exclude from gross income. Total
        #   household resources include "all income exempt or excluded from
        #   AGI" (book page 26). Since the federal list subtracts each from
        #   gross income, the excluded amount is entered in the income it
        #   comes from: savings bond interest in interest income (line 15,
        #   "including nontaxable interest"), adoption benefits, reported on
        #   Form W-2, in wages (line 14), and possession or Puerto Rico income
        #   in the source that earned it. Line 30 leaves it there.
        # The Schedule 1 is the claimant's own (MCL 206.508(3)): a person-level
        # adjustment, such as a dependent's IRA contribution, early withdrawal
        # penalty or educator expenses, is summed over the head and spouse, as
        # above_the_line_deductions does. A tax-unit-level adjustment already
        # describes the filer's return.
        ald = parameters(period).gov.irs.ald
        adjustments = tax_unit_non_dep_add(
            tax_unit,
            period,
            [
                deduction
                for deduction in p.household_resources_adjustments
                if deduction in ald.deductions
            ],
            include_dependents=ald.filer_amounts_recorded_on_dependents,
        )
        # Line 31: health insurance premiums.
        health_insurance_premiums = add(tax_unit, period, ["health_insurance_premiums"])
        return max_(0, total - adjustments - health_insurance_premiums)
