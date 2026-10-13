from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)
from policyengine_us.variables.household.expense.housing.tenure_type import (
    TenureType,
)


def _ism_exempt(person, period):
    """No ISM for a client who resides in and owns their home, receives
    subsidized housing or is homeless (9 CCR 2503-5 3.520.79(B)(1)-(3);
    9 CCR 2503-1 3.250.22(A), (B), (G) before 2014), or whose room and board
    is furnished during medical confinement: exempt income when a third
    party pays, and not in-kind support when the client does (3.520.786(B);
    3.250.32 before 2014)."""
    tenure = person.household("tenure_type", period.this_year)
    owned = (tenure == TenureType.OWNED_OUTRIGHT) | (
        tenure == TenureType.OWNED_WITH_MORTGAGE
    )
    in_another_household = person("ssi_lives_in_another_persons_household", period)
    owns_home = owned & ~in_another_household
    subsidized = person.spm_unit("receives_housing_assistance", period.this_year)
    homeless = person.household("is_homeless", period.this_year)
    medical_confinement = person("ssi_lives_in_medical_treatment_facility", period)
    return owns_home | subsidized | homeless | medical_confinement


def _colorado_shelter_ism(person, period, maximum):
    """ISM for shelter as Colorado computes it.

    3.520.79(A), (C) (3.250.22 and 3.250.221 before 2014). Colorado's amount
    depends on what the client pays, not on what the shelter is worth: the
    maximum less the client's payment ((C)(1)), the lesser of the fair share
    and the maximum less the payment ((C)(2)), or, for a client "paying no
    shelter costs", the maximum ((C)(3)). PolicyEngine has no input for the
    client's payment, the fair share or the market value, so a client who
    receives shelter from others is taken to pay none and is counted the
    maximum.
    """
    receives_shelter = person(
        "ssi_receives_shelter_from_others_in_household", period
    ) | person("ssi_receives_outside_shelter_support", period)
    return where(receives_shelter & ~_ism_exempt(person, period), maximum, 0)


def _ssa_ism(person, period, parameters):
    """The in-kind support and maintenance SSA counts for an SSI recipient.

    Under the presumed maximum value rule (20 CFR 416.1140) this is
    ssi_in_kind_support_and_maintenance, which holds a couple's presumed
    maximum value for each spouse; SSI splits it equally. Under the
    one-third reduction rule SSA counts "one-third of the Federal benefit
    rate as additional income" (20 CFR 416.1131(a)) for the individual, the
    couple or the individual with a deemed spouse; ssi_amount_if_eligible is
    the rate after that reduction.
    """
    pmv_ism = (
        person("ssi_in_kind_support_and_maintenance", period.this_year) / MONTHS_IN_YEAR
    )
    couple_computation = person("ssi_couple_computation_applies", period)
    pmv_ism = where(couple_computation, pmv_ism / 2, pmv_ism)
    arrangement = person("ssi_federal_living_arrangement", period)
    one_third_reduction_applies = (
        arrangement == SSIFederalLivingArrangement.ANOTHER_PERSONS_HOUSEHOLD
    )
    rate = parameters(period).gov.ssa.ssi.amount.one_third_reduction_rate
    reduced_rate = person("ssi_amount_if_eligible", period)
    one_third = reduced_rate * rate / (1 - rate)
    return where(one_third_reduction_applies, one_third, pmv_ism)


class co_ssa_in_kind_support_and_maintenance(Variable):
    value_type = float
    entity = Person
    label = "Colorado Adult Financial in-kind support and maintenance"
    documentation = "In-kind support and maintenance that Colorado counts as unearned income of an Old Age Pension or Aid to the Needy Disabled-Colorado Supplement client."
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CO
    reference = (
        # 3.520.71(E), PDF page 44; 3.520.79, PDF pages 72-74
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=9+CCR+2503-5&ruleVersionId=12428#page=72",
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=9+CCR+2503-5&ruleVersionId=12428#page=44",
        # 3.520.786(B), PDF page 71
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=9+CCR+2503-5&ruleVersionId=12428#page=71",
        # 3.250.22, 3.250.222, 3.250.32 before 2014
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=9+CCR+2503-2&ruleVersionId=4793#page=30",
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=9+CCR+2503-4&ruleVersionId=4795#page=13",
    )

    def formula_2007(person, period, parameters):
        # 9 CCR 2503-1 3.250.22 (9 CCR 2503-2 from September 2012): ISM for
        # shelter is capped at the shelter and utility component of the
        # grant standard, and 3.250.222 counts food supplied in full at its
        # component (3.460.43, 3.460.45). PolicyEngine models OAP only from
        # 2023, so the AND-CS standard's components are used. The rule
        # counted ISM before 2007 too, but the table effective January 1,
        # 2004 prints a $513 AND/SSI-CS maximum grant where the grant
        # standard is $601, so the base for 2002-2006 is unsettled and those
        # years are not modeled.
        p = parameters(period).gov.states.co.ssa
        standard = p.state_supplement.grant_standard
        share = p.ism.component_share
        shelter = _colorado_shelter_ism(person, period, share.shelter * standard)
        food_supplied_in_full = person("ssi_others_pay_all_meals", period)
        food = where(
            food_supplied_in_full & ~_ism_exempt(person, period),
            share.food * standard,
            0,
        )
        return shelter + food

    def formula_2014(person, period, parameters):
        # From January 1, 2014 the shelter cap is one-third of the SSI
        # benefit standard plus $20 (9 CCR 2503-4 3.460.45), and food is no
        # longer counted.
        maximum = parameters(period).gov.states.co.ssa.ism.maximum
        return _colorado_shelter_ism(person, period, maximum)

    def formula_2014_03(person, period, parameters):
        # 3.520.79(B)(6) and 3.520.71(E), effective March 2, 2014 and applied
        # from the March 2014 month: an SSI recipient whom SSA charges ISM is
        # charged "a matching ISM" ("an identical ISM amount"). With
        # PolicyEngine's inputs SSA charges ISM whenever 3.520.79(C) would,
        # except to a child in the parental household (whom SSI deems
        # instead) or a medical facility resident, so SSI recipients are
        # charged SSA's ISM. Other clients' ISM follows 3.520.79(C).
        maximum = parameters(period).gov.states.co.ssa.ism.maximum
        colorado = _colorado_shelter_ism(person, period, maximum)
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        return where(receives_ssi, _ssa_ism(person, period, parameters), colorado)
