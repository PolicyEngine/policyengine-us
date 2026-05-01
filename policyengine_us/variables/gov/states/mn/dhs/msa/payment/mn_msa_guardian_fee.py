from policyengine_us.model_api import *


class mn_msa_guardian_fee(Variable):
    value_type = float
    entity = Person
    label = "Minnesota Supplemental Aid guardian or conservator fee allowance"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/mn.html",
    )

    def formula(person, period, parameters):
        # Per SSA 2011 Minnesota Section 9.5: MSA pays the lesser of
        # 5% of gross monthly income or $100 to recipients with a
        # court-appointed guardian or conservator.
        p = parameters(period).gov.states.mn.dhs.msa.special_needs.guardian_fee
        has_guardian = person("mn_msa_has_guardian", period)
        gross = person("mn_msa_gross_income", period)
        return has_guardian * min_(gross * p.rate, p.max_amount)
