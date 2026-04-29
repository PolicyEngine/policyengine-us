from policyengine_us.model_api import *


class ct_ssp_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Connecticut SSP income eligible"
    definition_period = MONTH
    defined_for = StateCode.CT
    reference = (
        "https://www.cga.ct.gov/current/pub/chap_319s.htm#sec_17b-600",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ct.html",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ct.dss.ssp.eligibility
        ssi_fbr = parameters(period).gov.ssa.ssi.amount.individual

        # Per CGS 17b-600: Gross income cannot exceed 300% of SSI FBR.
        gross_income = person("ct_ssp_gross_income", period)
        income_cap = ssi_fbr * p.income_cap_rate
        countable_income = person("ct_ssp_countable_income", period)
        need_standard = person("ct_ssp_need_standard", period)

        return (gross_income <= income_cap) & (countable_income <= need_standard)
