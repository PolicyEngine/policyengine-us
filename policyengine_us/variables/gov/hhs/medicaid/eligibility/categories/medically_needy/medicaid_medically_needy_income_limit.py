from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class medicaid_medically_needy_income_limit(Variable):
    value_type = float
    entity = Person
    label = "Medicaid medically needy income limit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-42/section-435.811",
        "https://www.ecfr.gov/current/title-42/section-435.602",
    )

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.medically_needy.limit.income
        state = person.household("state_code_str", period)
        # SSI financial responsibility rules (42 CFR 435.602): the unit is
        # the individual or the married couple, not the tax filing unit.
        is_couple = person.marital_unit.nb_persons() == 2
        # Some states apply the one-person limit to a couple.
        same_limit = p.couple_uses_individual_limit[state].astype(bool)
        uses_couple_limit = is_couple & ~same_limit
        dollar_limit = where(uses_couple_limit, p.couple[state], p.individual[state])
        state_group = person.household("state_group_str", period)
        unit_fpg = fpg(where(uses_couple_limit, 2, 1), state_group, period, parameters)
        ssi = parameters(period).gov.ssa.ssi.amount
        fbr = where(uses_couple_limit, ssi.couple, ssi.individual)
        fpg_rate = p.fpg_rate[state]
        ssi_rate = p.ssi_rate[state]
        fpg_limit = fpg_rate * unit_fpg
        # Some states publish the monthly level in whole dollars. Fix the
        # monthly amount at cent precision first, so floating-point noise
        # cannot move an exact whole dollar (as in medicaid_income_level).
        fpg_monthly = np.round(fpg_limit / MONTHS_IN_YEAR, 2)
        # Illinois is the only state that drops the cents.
        rounds_down = (state == "IL") & p.il.rounds_down_monthly
        fpg_limit = select(
            [
                p.rounds_up_monthly[state].astype(bool),
                rounds_down,
            ],
            [
                np.ceil(fpg_monthly) * MONTHS_IN_YEAR,
                np.floor(fpg_monthly) * MONTHS_IN_YEAR,
            ],
            default=fpg_limit,
        )
        return select(
            [fpg_rate > 0, ssi_rate > 0],
            [
                fpg_limit,
                ssi_rate * fbr * MONTHS_IN_YEAR,
            ],
            default=dollar_limit * MONTHS_IN_YEAR,
        )
