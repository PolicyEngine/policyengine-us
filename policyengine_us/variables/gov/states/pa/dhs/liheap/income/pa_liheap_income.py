from policyengine_us.model_api import *


class pa_liheap_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Pennsylvania LIHEAP annual countable household income"
    defined_for = StateCode.PA
    reference = (
        # Sections 601.81-601.84, physical pages 49-54 and 46-51 respectively.
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dhs/documents/services/assistance/documents/heating-assistance_liheap/2026-liheap-state-plan.pdf#page=49",
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dhs/documents/services/assistance/documents/heating-assistance_liheap/2027-liheap-state-plan.pdf#page=46",
        # Section 1.9 checks "Excluding MediCare deduction" in FY2026 and FY2025.
        "https://liheapch.acf.gov/docs/2026/state-plans/PA_Plan_2026.pdf#page=6",
        "https://liheapch.acf.gov/docs/2025/state-plans/PA_Plan_2025.pdf#page=6",
        # Handbook 650.3(9) and 650.6(10), followed over the plan where they differ.
        "http://services.dpw.state.pa.us/oimpolicymanuals/liheap/650_Income/650.3_Countable_Unearned_Income.htm",
        "http://services.dpw.state.pa.us/OIMPolicyManuals/OIMArchive/2026-1/LIHEAP/650_Income/650.6_Income_Exclusions.htm",
        "http://services.dpw.state.pa.us/oimpolicymanuals/liheap/650_Income/650.6_Income_Exclusions.htm",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.pa.dhs.liheap.income
        person = spm_unit.members
        wages = add(spm_unit, period, ["pa_liheap_countable_employment_income"])
        # Section 601.82(2)(ii) forbids one source's loss offsetting another, so
        # each business and unearned source, including rent, is floored at zero.
        # Business inputs are already net; no second business-cost deduction.
        # Dependent children's business and unearned income count, as does
        # nonqualified members' income.
        other = 0
        for source in [*p.sources.business, *p.sources.unearned]:
            other = other + max_(person(source, period), 0)
        # Handbook 650.6(10) excludes "Medicare premiums deducted from Social
        # Security, Railroad Retirement, and other benefit payments." Plan
        # section 601.84(10) (FY2026 page 52, FY2027 page 50) and 55 Pa. Code
        # 601.84(10) name only Social Security; the handbook governs. Railroad
        # annuities are pensions under section 601.82(4)(viii). The one premium
        # is netted once from the two benefits combined, floored at zero, so it
        # reduces no other income. medicare_part_b_premium is zero for a person
        # who is not enrolled and excludes the share a Medicare Savings Program
        # pays, which is not withheld from the check. No Part D premium is
        # modeled, and no input isolates other annuities that withhold it.
        premium = person("medicare_part_b_premium", period)
        benefits = add(person, period, ["social_security", "railroad_benefits"])
        net_benefits = max_(benefits - premium, 0)
        # Handbook 650.3(9) counts "Interest and dividends from investments or
        # bank accounts of more than $25 per month"; plan section 601.82(4)(ix)
        # (FY2026 page 51, FY2027 page 48) sets no threshold. The handbook
        # governs. Its income test is household income (650.1), so the $25 is
        # applied once to the household's combined interest and dividends,
        # assuming steady monthly receipt. A per-person reading would subtract
        # $25 for each member with such income. Interest and dividends share
        # one $25 because 650.3(9) lists "Interest and dividends" as a single
        # item; applying $25 to each separately is the other reading (it would
        # lower income Case 4 from 9,660 to 9,600).
        investment = add(
            spm_unit, period, ["interest_income", "ordinary_dividend_income"]
        )
        investment_disregard = p.monthly_interest_dividend_disregard * MONTHS_IN_YEAR
        countable_investment = max_(investment - investment_disregard, 0)
        # Section 601.82(4)(i) counts public assistance grants received. The
        # annual tanf aggregate includes pa_tanf and applies take-up; pa_tanf
        # alone is the grant a nonrecipient could get.
        tanf = spm_unit("tanf", period)
        children = spm_unit.sum(person("age", period) < p.child_age_limit)
        child_support = add(spm_unit, period, ["child_support_received"])
        alimony = add(spm_unit, period, ["alimony_income"])
        child_exclusion = min_(
            child_support,
            p.support.monthly_child_disregard.calc(children) * MONTHS_IN_YEAR,
        )
        spousal_exclusion = min_(
            alimony, p.support.monthly_spousal_disregard * MONTHS_IN_YEAR
        )
        # Under the annual steady-receipt approximation, only the larger of
        # the child and spousal exclusions applies, not the sum of both caps.
        support_exclusion = max_(child_exclusion, spousal_exclusion)
        # Annual income does not reproduce the applicant's prior-month election.
        # Financial assistance counts cash help from friends or relatives.
        # Existing inputs cannot fully identify direct utility allowances,
        # CD/stock-sale proceeds, same-household support/rent, or refunded
        # support. Capital gains cannot proxy proceeds.
        counted = (
            wages + spm_unit.sum(other + net_benefits) + countable_investment + tanf
        )
        return max_(counted - support_exclusion, 0)
