from policyengine_us.model_api import *


class mn_msa_gross_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Minnesota Supplemental Aid gross income eligible"
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.dhs.state.mn.us/main/idcplg?IdcService=GET_DYNAMIC_CONVERSION&RevisionSelectionMethod=LatestReleased&dDocName=cm_001906",
        "https://www.house.mn.gov/hrd/pubs/pap_MSA.pdf#page=3",
    )

    def formula(person, period, parameters):
        # Per CM 0019.06, gross income may not exceed 300% of the federal
        # SSI individual benefit rate for an individual or 600% for a couple
        # where both spouses are MSA-categorically eligible.
        p = parameters(period).gov.states.mn.dhs.msa.eligibility.income_limit
        ssi_fbr = parameters(period).gov.ssa.ssi.amount.individual
        categorically_eligible = person("is_ssi_aged_blind_disabled", period.this_year)
        both_eligible = person.marital_unit.sum(categorically_eligible) == 2
        gross = add(
            person,
            period,
            [
                "ssi_earned_income",
                "ssi_unearned_income",
                "ssi_earned_income_deemed_from_ineligible_spouse",
                "ssi_unearned_income_deemed_from_ineligible_spouse",
                "ssi_unearned_income_deemed_from_ineligible_parent",
            ],
        )
        income = where(both_eligible, person.marital_unit.sum(gross), gross)
        cap = ssi_fbr * where(
            both_eligible, p.couple_fbr_multiplier, p.individual_fbr_multiplier
        )
        return income <= cap
