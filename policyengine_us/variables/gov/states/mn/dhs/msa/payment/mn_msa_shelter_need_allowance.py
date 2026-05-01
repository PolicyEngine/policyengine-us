from policyengine_us.model_api import *


class mn_msa_shelter_need_allowance(Variable):
    value_type = float
    entity = Person
    label = "Minnesota Supplemental Aid shelter-need special allowance"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/mn.html",
    )

    def formula(person, period, parameters):
        # Per Minn. Stat. § 256D.44 Subd. 5(g): the shelter-need
        # allowance equals one half of the federal SSI individual
        # benefit rate, adjusted annually on July 1.
        p = parameters(period).gov.states.mn.dhs.msa.special_needs.shelter_need
        ssi_fbr = parameters(period).gov.ssa.ssi.amount.individual
        eligible = person("mn_msa_shelter_need_eligible", period)
        return eligible * ssi_fbr * p.fbr_multiplier
