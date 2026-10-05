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
        # 2025 MI-1040 book: "Total Household Resources" (page 26) and
        # MI-1040CR lines 14 to 17 (page 31) and 18 to 31 (pages 32 and 33).
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/"
        "Forms/IIT/TY2025/MI-1040-Book.pdf#page=26",
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

        # MCL 206.508(3): "'Household' means a claimant and spouse", and
        # (4) counts "all income received by all persons of a household".
        # The MI-1040CR says "Include all taxable and nontaxable income you
        # and your spouse received" (2025 MI-1040 book, page 31). A
        # dependent's own income belongs on the dependent's return, so a
        # source is summed over the head and spouse only, as in
        # irs_gross_income. A tax-unit-level source (other_net_gain,
        # filer_loss_limited_net_capital_gains) already describes the
        # filer's return.
        # The form counts amounts the claimant receives for others in the
        # household on three lines (page 32), so these are summed over every
        # member:
        # Line 21: Social Security, SSI and railroad retirement benefits,
        # including "amounts received for minor children or other dependent
        # adults who live with you".
        # Line 22: "child support and all payments received as a foster
        # parent".
        # Line 27: "the total payments made to your household by MDHHS and
        # all other public assistance payments". A Family Independence
        # Program grant covers the children in the case, and tanf, an SPM
        # unit amount, reaches the tax unit in per-person shares.
        received_for_household = {
            "social_security",
            "ssi",
            "railroad_benefits",
            "child_support_received",
            "tanf",
            "general_assistance",
            "gi_cash_assistance",
        }

        business_income = 0
        rental_income = 0
        other_income = 0
        for source in p.household_resources:
            if source in received_for_household:
                amount = add(tax_unit, period, [source])
            else:
                amount = tax_unit_non_dep_add(tax_unit, period, [source])
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
        # The Schedule 1 is the claimant's own: a dependent's adjustments,
        # like the dependent's income, are on the dependent's return. The
        # self-employment adjustments are computed per person, so their
        # person-level amounts are summed over the head and spouse.
        per_person_adjustments = {
            "self_employment_tax_ald",
            "self_employed_health_insurance_ald",
            "self_employed_pension_contribution_ald",
        }
        adjustments = tax_unit_non_dep_add(
            tax_unit,
            period,
            [
                (
                    f"{deduction}_person"
                    if deduction in per_person_adjustments
                    else deduction
                )
                for deduction in parameters(period).gov.irs.ald.deductions
                if deduction != "loss_ald"
            ],
        )
        # Line 31: "insurance premiums you paid for yourself and your
        # family". MCL 206.510(1) lets a person deduct "the amount that
        # person paid in premiums ... for that insurance plan for the
        # person's family", so every member's premiums count.
        health_insurance_premiums = add(tax_unit, period, ["health_insurance_premiums"])
        return max_(0, total - adjustments - health_insurance_premiums)
