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
        "net of the Medicare Part B premium; SSI counts in full. Paid child "
        "support is not deducted. Exempt subtypes and receipts without existing "
        "inputs are not reconstructed. Supply adjusted countable income directly "
        "when the detailed program amount is known."
    )
    reference = (
        # Section 1.9, PDF pages 5-7.
        "https://liheapch.acf.gov/docs/2026/state-plans/WA_Plan_2026.pdf#page=5",
        # FY2025-26 application, PDF pages 1-2,13.
        "https://drive.google.com/file/d/18fvR5CL8UKpTj4Vsm7KlkitKUJclAvkR/view#page=1",
        # Policy 1.1.2 incorporates LIHEAP income rules, PDF pages 14-15.
        "https://deptofcommerce.app.box.com/s/5a32797ex8tz2blo8nwtifecokpya37j#page=14",
    )
    defined_for = StateCode.WA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wa.commerce.liheap.income
        person = spm_unit.members
        wages = max_(person("employment_income", period), 0)
        business = sum(max_(person(source, period), 0) for source in p.business_sources)
        # Net inputs approximate allowable business expenses; the 50% standard
        # expense option and 20% wage deduction are not applied again.
        # Annual net inputs cannot reproduce separate monthly loss floors.
        earned = where(
            person("age", period) >= p.earned_income_min_age,
            wages * (1 - p.wage_deduction_rate) + business,
            0,
        )
        retirement = sum(
            max_(person(source, period), 0) for source in p.retirement_sources
        )
        unemployment = max_(person("total_unemployment_compensation", period), 0)
        unearned = sum(max_(person(source, period), 0) for source in p.unearned_sources)
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
        # Each SPM-level cash payment is included once, not once per member.
        # General assistance input represents other assistance, such as ABD.
        assistance = add(spm_unit, period, ["tanf", "wa_sfa"])
        # Income comes from the plan and Commerce manual, which list no
        # deduction for child support paid. The CACLMT subgrantee FAQ deducts
        # child support paid; not modeled (https://www.liheapcalendar.com/CACLMT/FAQ).
        return spm_unit.sum(personal_income) + max_(assistance, 0)
