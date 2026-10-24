from policyengine_us.model_api import *


class va_eap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Virginia EAP countable income"
    documentation = (
        "Annual gross earned and unearned income of all household members, including "
        "members who are not citizens or qualified aliens, less $50 a month for each "
        "elderly or disabled member and less each member's out-of-pocket Medicare Part "
        "B premium. Manual exemption 15 (Complete_Manual.pdf#page=30) exempts "
        "'Medicare Premiums when deducted from Social Security or Railroad Retirement "
        "checks or when the household member is responsible for payment of the "
        "premium' and has them deducted from gross income; Part D has no premium "
        "variable and is not deducted. Earned income of members under 18 is exempt. "
        "Each earned and unearned source is floored at zero, so a business or rental "
        "loss does not offset other income. Annual amounts stand for twelve times the "
        "prior month's income; the weekly and biweekly conversions, per-member "
        "rounding, roomer and boarder profit rules and the other exemptions without an "
        "input are not modeled."
    )
    reference = (
        # PDF pages 28-31, 37-41, 52
        "https://www.dss.virginia.gov/media/vdss/benefit-programs/documents/eap/Complete_Manual.pdf#page=28",
        # PDF pages 5-6
        "https://liheapch.acf.gov/docs/2026/state-plans/VA_Plan_2026.pdf#page=5",
    )
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.va.dss.eap
        person = spm_unit.members
        age = person("age", period)
        # Manual C.5.a.3: gross earnings and self-employment profit count.
        earned = 0
        for source in p.income.sources.earned:
            earned = earned + max_(person(source, period), 0)
        # Exemption 20: "Earned income (regardless of amount) of dependent
        # children under 18 years of age".
        adult_earned = where(age >= p.income.child_earnings_age_limit, earned, 0)
        # C.5.a.3 counts income received and C.5.a.4.b lists rental property
        # among the self-employment profit determinations, so each unearned
        # source is floored like the earned sources: a rental loss does not
        # offset other income.
        unearned = 0
        for source in p.income.sources.unearned:
            # ADD sums the MONTH-defined ssi and va_ag over the year.
            unearned = unearned + max_(person(source, period, options=[ADD]), 0)
        # TANF the household receives: the take-up-gated aggregate, which
        # includes va_tanf.
        tanf = spm_unit("tanf", period)
        gross_income = spm_unit.sum(adult_earned + unearned) + tanf
        # Manual B.6.b exemption 15 (Complete_Manual.pdf#page=30): "Medicare
        # Premiums when deducted from Social Security or Railroad Retirement
        # checks or when the household member is responsible for payment of
        # the premium. NOTE: This is not an automatic exemption and therefore
        # must be manually deducted from gross income." Plan Section 1.9 counts
        # SSA benefits "Excluding MediCare deduction". medicare_part_b_premium
        # is each member's out-of-pocket Part B premium, zero when a Medicare
        # Savings Program pays it; no Part D premium variable exists.
        medicare_premiums = add(spm_unit, period, ["medicare_part_b_premium"])
        # Manual B.6.c: "$50.00 per elderly or disabled individual is deducted
        # from the total gross income of the household ... If an individual is
        # both aged and disabled, only one $50 deduction will be given".
        disregard_members = spm_unit.sum(
            (age >= p.age.elderly) | person("va_eap_disabled", period)
        )
        disregard = disregard_members * p.income.medical_disregard * MONTHS_IN_YEAR
        return max_(gross_income - medicare_premiums - disregard, 0)
