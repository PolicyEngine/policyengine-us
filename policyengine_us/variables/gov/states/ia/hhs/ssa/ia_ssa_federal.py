from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi._ssi_state_supplement import (
    ssi_state_supplement,
)


class ia_ssa_federal(Variable):
    value_type = float
    entity = Person
    label = "Federally administered Iowa State Supplementary Assistance"
    definition_period = MONTH
    unit = USD
    reference = (
        # 441 IAC 52.1(1), (2) and (4); PDF pages 1-2
        "https://www.legis.iowa.gov/docs/iac/chapter/441.52.pdf#page=1",
        # 441 IAC 51.5(1)
        "https://www.legis.iowa.gov/docs/iac/chapter/441.51.pdf#page=2",
        # PDF pages 20, 24-28, 30, 34-35
        "https://hhs.iowa.gov/media/3987/download?inline=#page=20",
        "https://secure.ssa.gov/poms.nsf/lnx/0501415058#f",
    )
    defined_for = "ia_ssa_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ia.hhs.ssa
        ssi = parameters(period).gov.ssa.ssi
        category = person("ia_ssa_category", period)
        c = category.possible_values
        # NOTE: The joint-couple test uses the federal definition, which treats
        # an aged, blind or disabled spouse who is ineligible for SSI or does
        # not apply as part of a joint claim (issue 10138).
        joint = person("ssi_couple_computation_applies", period)
        blind = person("is_blind", period.this_year)
        blind_count = person.marital_unit.sum(blind)
        dependent = person("ia_ssa_dependent_countable_income", period)
        dependent = where(joint, person.marital_unit.max(dependent), dependent)
        recipient_income = person("ssi_countable_income", period) + person(
            "ssi", period
        )
        group_income = (
            where(joint, person.marital_unit.sum(recipient_income), recipient_income)
            + dependent
        )
        need = (
            where(
                joint,
                ssi.amount.couple + blind_count * p.blind_amount,
                ssi.amount.individual + blind * p.blind_amount,
            )
            + p.dependent_amount
        )
        # NOTE: 6-B p.24 excludes as a dependent "A person whose countable
        # income is more than $518 per month", which would admit income of
        # exactly $518. 6-B p.25 ("The dependent must have countable income of
        # less than $518 per month") and 441 IAC 51.5(1) ("must be less than
        # the amount established by the department") exclude it. The model
        # follows 51.5(1) and p.25 (ia_ssa.yaml Case 3).
        # The dependent-person standards are couple standards (441 IAC
        # 52.1(2)"b", "d" and "e"), so certifying either spouse of an eligible
        # couple applies the couple level (integration.yaml Cases 11-12),
        # whatever the other spouse's category.
        certified = category == c.DEPENDENT_PERSON
        certified = where(joint, person.marital_unit.any(certified), certified)
        dp = certified & (dependent < p.dependent_amount) & (group_income < need)
        # 6-B: the family-life home standard is "$1,156", and the maximum
        # supplement is "$162 ($1,156 - $994 SSI standard)". SSA pays at most
        # $142 because it applies the $20 general exclusion. The couple amount
        # is twice the standard less the SSI couple rate and $20 (POMS code D
        # Aged/Aged $801), so the standard and the couple amount move with the
        # federal benefit rate.
        general = ssi.income.exclusions.general
        family_life_need = ssi.amount.individual + p.family_life_supplement
        flh = (category == c.FAMILY_LIFE_HOME) & (
            person("ia_ssa_care_countable_income", period) < family_life_need
        )
        family_life_individual = p.family_life_supplement - general
        family_life_couple = 2 * family_life_need - ssi.amount.couple - general
        federal_la = person("ssi_federal_living_arrangement", period)
        medical = federal_la == federal_la.possible_values.MEDICAL_TREATMENT_FACILITY
        # NOTE: 441 IAC 52.1(4) sets $22 as "The standard for a blind recipient
        # not receiving another type of state supplementary assistance". 6-B
        # Blind Supplement p.20 excludes the blind supplement "when determining
        # eligibility for other SSA programs the person may be receiving
        # simultaneously. For example, the blind supplement is not countable
        # income to determine client participation or eligibility for the RCF
        # supplement", and p.42 says "Do not count the $22 special blind
        # allowance when determining client participation" for in-home care.
        # POMS SI 01415.058 F.1 code A pays a blind recipient "who does not live
        # in any other State living arrangement variation", the SSA-coded
        # dependent-person and family-life home rows, whose levels include the
        # $22. The model follows the manual and POMS and pays the $22 with
        # residential care (ia_ssa.yaml Case 11) and in-home care
        # (integration.yaml Case 9).
        individual_rate = (
            dp * p.dependent_amount
            + flh * family_life_individual
            + blind * p.blind_amount
        )
        # NOTE: 6-B Income (DP) lists "Blind client, aged or disabled spouse, and
        # a dependent relative $2,031", a $540 supplement over the $1,491
        # couple rate. POMS SI 01415.058 F.2.b code C shows Aged/Blind 562.00
        # (2,053.00), which is the blind/blind level. The model follows the
        # manual and POMS F.1 code C ("increases by $22 for each blind
        # recipient"), adding $22 per blind spouse (integration.yaml Case 4).
        couple_rate = (
            dp * p.dependent_amount
            + flh * family_life_couple
            + 2 * blind * p.blind_amount
        )
        recipient = (individual_rate > 0) & ~medical & person("ia_ssa_eligible", period)
        count = person.marital_unit.sum(recipient)
        payment = ssi_state_supplement(
            person,
            period,
            parameters,
            individual_rate,
            couple_rate,
            federal_payment_rules=False,
        )
        # Only the blind member receives the ordinary categorical allowance.
        # DP/FLH couples share the combined payment without duplication.
        payment = where(joint, payment * 2 / max_(count, 1), payment) * recipient
        # SSA pays these rows, so its rounding and $1 minimum apply. The helper
        # would apply them before the redistribution above, so it returns the
        # unrounded amount and the same SSA rule is applied here afterwards
        # (SI 02001.005, SI 02001.010).
        rounded = np.ceil(np.floor(payment * 1000) / 10) / 100
        return where(
            rounded > 0, max_(rounded, ssi.state_supplement.minimum_payment), 0
        )
