from policyengine_us.model_api import *


class pell_grant(Variable):
    value_type = float
    entity = Person
    label = "Pell Grant"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        coa = person("cost_of_attending_college", period)
        months_in_school = person("pell_grant_months_in_school", period)
        efc = person("pell_grant_efc", period)
        sai = person("pell_grant_sai", period)
        eligibility = person("pell_grant_eligibility_type", period)
        uses_efc = person("pell_grant_uses_efc", period)
        uses_sai = person("pell_grant_uses_sai", period)
        p = parameters(period).gov.ed.pell_grant
        contribution = select([uses_efc, uses_sai], [efc, sai])
        unbounded = coa - contribution
        amount = where(unbounded < p.amount.min, 0, unbounded)
        uncapped_efc_pell = amount * (
            months_in_school / p.months_in_school_year
        )
        uncapped_sai_pell = select(
            [
                eligibility == eligibility.possible_values.INELIGIBLE,
                eligibility == eligibility.possible_values.MAXIMUM,
                eligibility == eligibility.possible_values.MINIMUM,
            ],
            [0, p.amount.max, amount],
        )
        uncapped = select(
            [uses_efc, uses_sai], [uncapped_efc_pell, uncapped_sai_pell]
        )
        max = min_(coa, p.amount.max)
        return min_(max, uncapped)
