from policyengine_us.model_api import *


class va_eap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Virginia EAP countable income"
    documentation = (
        "Annual gross earned and unearned income of all household members, "
        "including members who are not citizens or qualified aliens, less $50 a "
        "month for each elderly or disabled member. Earned income of members "
        "under 18 is exempt. Each earned source is floored at zero, so a "
        "business loss does not offset other income. Annual amounts stand for "
        "twelve times the prior month's income; the weekly and biweekly "
        "conversions, per-member rounding, Medicare premium exemption, roomer "
        "and boarder profit rules and the other exemptions without an input "
        "are not modeled."
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
        # add() sums the MONTH-defined ssi over the year.
        unearned = add(spm_unit, period, p.income.sources.unearned)
        gross_income = spm_unit.sum(adult_earned) + unearned
        # Manual B.6.c: "$50.00 per elderly or disabled individual is deducted
        # from the total gross income of the household ... If an individual is
        # both aged and disabled, only one $50 deduction will be given".
        disregard_members = spm_unit.sum(
            (age >= p.age.elderly) | person("va_eap_disabled", period)
        )
        disregard = disregard_members * p.income.medical_disregard * MONTHS_IN_YEAR
        return max_(gross_income - disregard, 0)
