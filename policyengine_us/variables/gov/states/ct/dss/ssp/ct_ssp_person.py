from policyengine_us.model_api import *


class ct_ssp_person(Variable):
    value_type = float
    entity = Person
    label = "Connecticut State Supplement to the Aged, Blind or Disabled per person"
    unit = USD
    definition_period = MONTH
    defined_for = "ct_ssp_eligible_person"
    reference = (
        "https://www.cga.ct.gov/current/pub/chap_319s.htm#sec_17b-600",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ct.html",
    )

    def formula(person, period, parameters):
        need_standard = person("ct_ssp_need_standard", period)
        countable_income = person("ct_ssp_countable_income", period)
        return max_(need_standard - countable_income, 0)
