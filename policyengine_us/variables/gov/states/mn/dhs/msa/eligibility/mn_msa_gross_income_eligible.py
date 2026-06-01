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
        # where both spouses are MSA-categorically eligible. Per CM 0017,
        # for SSI recipients count the full SSI FBR as gross unearned
        # income (even when the actual SSI check is less).
        p = parameters(period).gov.states.mn.dhs.msa.eligibility.income_limit
        ssi_individual_fbr = parameters(period).gov.ssa.ssi.amount.individual
        categorically_eligible = person("is_ssi_aged_blind_disabled", period.this_year)
        both_eligible = person.marital_unit.sum(categorically_eligible) == 2
        income = add(
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
        ssi = person("ssi", period)
        ssi_fbr = person("ssi_amount_if_eligible", period)
        gross = income + where(ssi > 0, ssi_fbr, 0)
        au_income = where(both_eligible, person.marital_unit.sum(gross), gross)
        cap = ssi_individual_fbr * where(
            both_eligible, p.couple_fbr_multiplier, p.individual_fbr_multiplier
        )
        return au_income <= cap
