from policyengine_us.model_api import *


class mn_msa_gross_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Minnesota Supplemental Aid gross income eligible"
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.house.mn.gov/hrd/pubs/pap_MSA.pdf#page=2",
    )

    def formula(person, period, parameters):
        # Per Minn. Stat. § 256D.44 Subd. 1, gross income may not exceed
        # 300% of the federal SSI individual benefit rate for an
        # individual or 600% for a couple. The couple cap applies to
        # any married pair where both spouses are MSA-categorically
        # eligible — not just SSI joint filers.
        p = parameters(period).gov.states.mn.dhs.msa.eligibility.income_limit
        ssi_fbr = parameters(period).gov.ssa.ssi.amount.individual
        categorically_eligible = person("is_ssi_aged_blind_disabled", period.this_year)
        both_eligible = person.marital_unit.sum(categorically_eligible) == 2
        gross = person("mn_msa_gross_income", period)
        income = where(both_eligible, person.marital_unit.sum(gross), gross)
        cap = ssi_fbr * where(
            both_eligible, p.couple_fbr_multiplier, p.individual_fbr_multiplier
        )
        return income <= cap
