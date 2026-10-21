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
        "The retirement deduction covers pension income and retirement-account "
        "distributions. Social Security and SSI remain fully counted because "
        "their deduction treatment is unverified; this may overstate income. "
        "Medicare deductions, exempt subtypes and receipts without existing "
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
        "https://www.liheapcalendar.com/CACLMT/FAQ",
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
        personal_income = (
            earned
            + retirement * (1 - p.retirement_deduction_rate)
            + unemployment * (1 - p.unemployment_deduction_rate)
            + unearned
        )
        # Each SPM-level cash payment is included once, not once per member.
        # General assistance input represents other assistance, such as ABD.
        assistance = add(spm_unit, period, ["tanf", "wa_sfa"])
        support_paid = spm_unit.sum(max_(person("child_support_expense", period), 0))
        return max_(
            spm_unit.sum(personal_income) + max_(assistance, 0) - support_paid, 0
        )
