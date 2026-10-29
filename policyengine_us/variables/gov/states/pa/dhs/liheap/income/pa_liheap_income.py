from policyengine_us.model_api import *


class pa_liheap_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Pennsylvania LIHEAP annual countable household income"
    defined_for = StateCode.PA
    reference = (
        # Sections 601.81-601.84; PDF pages 49-54
        "https://web.archive.org/web/20251016232745/https://www.pa.gov/content/dam/copapwp-pagov/en/dhs/documents/services/assistance/documents/heating-assistance_liheap/2026-liheap-state-plan.pdf#page=49",
        # PDF pages 46-51
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dhs/documents/services/assistance/documents/heating-assistance_liheap/2027-liheap-state-plan.pdf#page=46",
        # Section 1.9 checks "Excluding MediCare deduction" in FY2026 and FY2025.
        "https://liheapch.acf.gov/docs/2026/state-plans/PA_Plan_2026.pdf#page=6",
        "https://liheapch.acf.gov/docs/2025/state-plans/PA_Plan_2025.pdf#page=6",
        "https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/055/chapter601/s601.82.html",
        "https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/055/chapter601/s601.84.html",
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
        # Section 601.84(10) of the plan (FY2026 page 52, FY2027 page 50) and of
        # 55 Pa. Code excludes Medicare premiums deducted from Social Security
        # benefit payments, so the premium is netted from Social Security only,
        # floored at zero, and reduces no other income. Railroad retirement
        # counts in full as a pension. medicare_part_b_premium is zero for a
        # person who is not enrolled and excludes the share a Medicare Savings
        # Program pays, which is not withheld from the check. No Part D premium
        # is modeled.
        premium = person("medicare_part_b_premium", period)
        social_security = person("social_security", period)
        net_social_security = max_(social_security - premium, 0)
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
        counted = wages + spm_unit.sum(other + net_social_security) + tanf
        return max_(counted - support_exclusion, 0)
