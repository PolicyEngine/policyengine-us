from policyengine_us.model_api import *


class wa_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Washington LIHEAP countable income"
    documentation = (
        "Annual income approximates the selectable application-period average. "
        "All members' otherwise countable income is retained, including members "
        "excluded from household size. Reported wages approximate earnings taxed "
        "at payout; existing net business income receives no further deduction. "
        "The retirement deduction covers pension income, retirement-account "
        "distributions and military retirement income. Social Security counts "
        "net of the Medicare Part B premium; SSI counts in full. TANF, State "
        "Family Assistance, Refugee Cash Assistance and the state supplement to "
        "SSI count as cash assistance. Child support and alimony paid by "
        "members are deducted, with countable income floored at zero. Exempt "
        "subtypes and receipts without existing inputs are not reconstructed. "
        "Supply adjusted countable income directly when the detailed program "
        "amount is known."
    )
    reference = (
        # Section 1.9, PDF pages 5-7.
        "https://liheapch.acf.gov/docs/2026/state-plans/WA_Plan_2026.pdf#page=5",
        # FY2025-26 application, PDF pages 1-2,13.
        "https://drive.google.com/file/d/18fvR5CL8UKpTj4Vsm7KlkitKUJclAvkR/view#page=1",
        # Policies 1.1.1-1.1.2 incorporate LIHEAP income rules; Exhibit 1.3.1A
        # lists child support received/paid. PDF pages 13-15,445.
        "https://deptofcommerce.app.box.com/s/5a32797ex8tz2blo8nwtifecokpya37j#page=13",
        "https://www.clarkpublicutilities.com/residential-customers/financial-assistance/all-financial-assistance-programs/liheap-income-requirements/",
        "https://www.liheapcalendar.com/CACLMT/FAQ",
    )
    defined_for = StateCode.WA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wa.commerce.liheap.income
        person = spm_unit.members
        wages = max_(person("employment_income", period), 0)
        business = 0
        for source in p.business_sources:
            business = business + max_(person(source, period), 0)
        # Net inputs approximate allowable business expenses; the 50% standard
        # expense option and 20% wage deduction are not applied again.
        # Annual net inputs cannot reproduce separate monthly loss floors.
        earned = where(
            person("age", period) >= p.earned_income_min_age,
            wages * (1 - p.wage_deduction_rate) + business,
            0,
        )
        retirement = 0
        for source in p.retirement_sources:
            retirement = retirement + max_(person(source, period), 0)
        unemployment = max_(person("total_unemployment_compensation", period), 0)
        unearned = 0
        for source in p.unearned_sources:
            unearned = unearned + max_(person(source, period), 0)
        # Plan section 1.9 checks "Excluding MediCare deduction" for Social
        # Security, so each person's benefit counts net of the Part B premium
        # that person pays. medicare_part_b_premium is zero for a person not
        # enrolled and excludes any share a Medicare Savings Program pays.
        social_security = max_(person("social_security", period), 0)
        premium = person("medicare_part_b_premium", period)
        net_social_security = max_(social_security - premium, 0)
        personal_income = (
            earned
            + retirement * (1 - p.retirement_deduction_rate)
            + unemployment * (1 - p.unemployment_deduction_rate)
            + unearned
            + net_social_security
        )
        # Plan section 1.8 counts gross income. State cash assistance counts
        # like the counted TANF, SFA and SSI: Refugee Cash Assistance (WAC
        # 388-400-0030) and the state supplement to SSI (WAC 388-474-0012(1)).
        # No Washington LIHEAP source names either program. The SPM-level
        # payments are added once, and the supplement is summed over members.
        # General assistance input represents other assistance, such as ABD.
        assistance = add(spm_unit, period, ["tanf", "wa_sfa", "wa_rca", "wa_ssp"])
        # Commerce Weatherization Manual Exhibit 1.3.1A, which Policy 1.1.1
        # ties to the LIHEAP income guidelines, lists "Child support
        # received/paid" as income documentation. Clark Public Utilities
        # deducts paid child support and alimony, and CACLMT deducts paid
        # child support.
        support_paid = add(
            spm_unit, period, ["child_support_expense", "alimony_expense"]
        )
        gross = spm_unit.sum(personal_income) + max_(assistance, 0)
        return max_(gross - max_(support_paid, 0), 0)
