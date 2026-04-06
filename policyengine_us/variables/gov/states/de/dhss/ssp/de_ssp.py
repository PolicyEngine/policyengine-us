from policyengine_us.model_api import *


class de_ssp(Variable):
    value_type = float
    entity = Person
    label = "Delaware State Supplementary Payment"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.DE
    reference = "https://secure.ssa.gov/poms.nsf/lnx/0501415008PHI"

    def formula(person, period, parameters):
        eligible = person("de_ssp_eligible", period)
        p = parameters(period).gov.states.de.dhss.ssp.amount
        joint_claim = person("ssi_claim_is_joint", period.this_year)
        both_eligible = person.marital_unit.sum(eligible) == 2
        is_couple = joint_claim & both_eligible
        per_person_amount = where(is_couple, p.couple / 2, p.individual)
        uncapped_ssi = person("uncapped_ssi", period)
        reduction = max_(0, -uncapped_ssi)
        supplement = max_(0, per_person_amount - reduction)
        return where(
            is_couple,
            person.marital_unit.sum(supplement) / 2,
            supplement * eligible,
        )
