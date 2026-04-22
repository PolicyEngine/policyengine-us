from policyengine_us.model_api import *


class ct_ssp_special_needs(Variable):
    value_type = float
    entity = Person
    label = "Connecticut SSP special needs allowance"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CT
    reference = (
        "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/fact-sheets-and-issue-briefs/fact-sheets/dss-program-standards-chart-effective-010126.pdf",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ct.html",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ct.dss.ssp.special_needs
        has_therapeutic_diet = person("ct_ssp_has_therapeutic_diet", period.this_year)
        return has_therapeutic_diet * p.therapeutic_diet
