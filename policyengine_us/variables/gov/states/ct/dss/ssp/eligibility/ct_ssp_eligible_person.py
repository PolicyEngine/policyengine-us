from policyengine_us.model_api import *


class ct_ssp_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for Connecticut State Supplement to the Aged, Blind or Disabled"
    definition_period = MONTH
    defined_for = StateCode.CT
    reference = (
        "https://www.cga.ct.gov/current/pub/chap_319s.htm#sec_17b-600",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ct.html",
    )

    def formula(person, period, parameters):
        categorically_eligible = person("ct_ssp_categorically_eligible", period)
        resource_eligible = person("ct_ssp_resource_eligible", period)
        income_eligible = person("ct_ssp_income_eligible", period)
        return categorically_eligible & resource_eligible & income_eligible
