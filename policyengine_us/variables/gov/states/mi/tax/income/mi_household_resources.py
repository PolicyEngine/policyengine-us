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
        # Line 17: U.S. Schedule E Parts I and V (rents, royalties and farm
        # rental income). "If the total is negative enter 0."
        rental_sources = {
            "rental_income",
            "farm_rent_income",
        }

        business_income = 0
        rental_income = 0
        other_income = 0
        for source in p.household_resources:
            amount = add(tax_unit, period, [source])
            if source in business_sources:
                business_income += amount
            elif source in rental_sources:
                rental_income += amount
            else:
                other_income += amount
        total = other_income + max_(business_income, 0) + max_(rental_income, 0)

        # Line 30: "total adjustments from your U.S. Form 1040, Schedule 1".
        # Business, rental and capital losses are income items (Schedule 1
        # Part I and Schedule D), not Part II adjustments. They are netted
        # and floored on lines 16, 17 and 19 above, so loss_ald, which holds
        # them, is left out.
        adjustments = add(
            tax_unit,
            period,
            [
                deduction
                for deduction in parameters(period).gov.irs.ald.deductions
                if deduction != "loss_ald"
            ],
        )
        # Line 31: health insurance premiums.
        health_insurance_premiums = add(tax_unit, period, ["health_insurance_premiums"])
        return max_(0, total - adjustments - health_insurance_premiums)
