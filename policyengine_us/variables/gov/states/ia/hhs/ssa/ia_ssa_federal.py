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
        "https://hhs.iowa.gov/media/3987/download?inline=",
        "https://secure.ssa.gov/poms.nsf/lnx/0501415058#f",
    )
    defined_for = "ia_ssa_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ia.hhs.ssa
        ssi = parameters(period).gov.ssa.ssi
        category = person("ia_ssa_category", period)
        c = category.possible_values
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
        dp = (
            (category == c.DEPENDENT_PERSON)
            & (dependent < p.dependent_amount)
            & (group_income < need)
        )
        flh = (category == c.FAMILY_LIFE_HOME) & (
            person("ia_ssa_care_countable_income", period) < p.family_life_need
        )
        federal_la = person("ssi_federal_living_arrangement", period)
        medical = federal_la == federal_la.possible_values.MEDICAL_TREATMENT_FACILITY
        individual_rate = (
            dp * p.dependent_amount
            + flh * p.family_life_individual_amount
            + blind * p.blind_amount
        )
        # The state manual and SSA's category definition add $22 per blind
        # spouse. The SSA table's mixed-category C rows show an inconsistent
        # $44 increment; use the explicitly stated per-blind-person rule.
        couple_rate = (
            dp * p.dependent_amount
            + flh * p.family_life_couple_amount
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
        rounded = np.ceil(np.floor(payment * 1000) / 10) / 100
        return where(
            rounded > 0, max_(rounded, ssi.state_supplement.minimum_payment), 0
        )
