from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class medicaid_medically_needy_income_limit(Variable):
    value_type = float
    entity = Person
    label = "Medicaid medically needy income limit"
    documentation = (
        "Annual medically needy income limit for an individual or a married "
        "couple. States set it as a dollar amount, a share of the federal "
        "poverty guideline, or a share of the SSI federal benefit rate."
    )
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
        # Washington applies its one-person limit to a couple.
        same_limit = p.couple_uses_individual_limit[state].astype(bool)
        uses_couple_limit = is_couple & ~same_limit
        dollar_limit = where(uses_couple_limit, p.couple[state], p.individual[state])
        state_group = person.household("state_group_str", period)
        unit_fpg = fpg(where(uses_couple_limit, 2, 1), state_group, period, parameters)
        ssi = parameters(period).gov.ssa.ssi.amount
        fbr = where(uses_couple_limit, ssi.couple, ssi.individual)
        fpg_rate = p.fpg_rate[state]
        ssi_rate = p.ssi_rate[state]
        return select(
            [fpg_rate > 0, ssi_rate > 0],
            [
                fpg_rate * unit_fpg,
                ssi_rate * fbr * MONTHS_IN_YEAR,
            ],
            default=dollar_limit * MONTHS_IN_YEAR,
        )
