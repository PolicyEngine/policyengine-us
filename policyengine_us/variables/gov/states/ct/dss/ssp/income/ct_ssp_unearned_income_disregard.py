from policyengine_us.model_api import *


class ct_ssp_unearned_income_disregard(Variable):
    value_type = float
    entity = Person
    label = "Connecticut SSP unearned income disregard"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CT
    reference = (
        "https://www.ctdssmap.com/CTPortal/Information/Get/UPM#5030.15",
        "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/fact-sheets-and-issue-briefs/fact-sheets/dss-program-standards-chart-effective-010126.pdf",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ct.html",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ct.dss.ssp.disregard
        arrangement = person("ct_ssp_living_arrangement", period.this_year)
        return p.unearned[arrangement]
