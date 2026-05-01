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
        # individual or 600% for a couple.
        p = parameters(period).gov.states.mn.dhs.msa.eligibility.income_limit
        ssi_fbr = parameters(period).gov.ssa.ssi.amount.individual
        joint_claim = person("ssi_claim_is_joint", period.this_year)
        categorically_eligible = person("mn_msa_categorically_eligible", period)
        both_eligible = (
            person.marital_unit.sum(categorically_eligible) == 2
        ) & joint_claim
        gross = person("mn_msa_gross_income", period)
        couple_gross = person.marital_unit.sum(gross)
        income = where(both_eligible, couple_gross, gross)
        cap = where(
            both_eligible,
            ssi_fbr * p.couple_fbr_multiplier,
            ssi_fbr * p.individual_fbr_multiplier,
        )
        return income <= cap
