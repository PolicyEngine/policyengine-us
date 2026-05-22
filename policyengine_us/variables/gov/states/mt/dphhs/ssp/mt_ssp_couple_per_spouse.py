from policyengine_us.model_api import *


class mt_ssp_couple_per_spouse(Variable):
    value_type = float
    entity = Person
    label = "Montana SSP couple payment amount per spouse"
    unit = USD
    definition_period = MONTH
    defined_for = "mt_ssp_eligible"
    reference = (
        "https://secure.ssa.gov/poms.nsf/lnx/0501415010DEN",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/mt.html",
    )

    def formula(person, period, parameters):
        joint_claim = person("ssi_claim_is_joint", period.this_year)
        eligible = person("mt_ssp_eligible", period)
        both_eligible = person.marital_unit.sum(eligible) == 2
        is_couple = person.marital_unit.nb_persons() == 2
        category = person("mt_ssp_payment_category", period)
        shared_category = person.marital_unit.max(category) == person.marital_unit.min(
            category
        )
        couple_gate = joint_claim & both_eligible & is_couple & shared_category
        p = parameters(period).gov.states.mt.dphhs.ssp
        return where(couple_gate, p.amount.couple[category] / 2, 0)
