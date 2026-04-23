from policyengine_us.model_api import *


class ct_ssp_shelter_allowance(Variable):
    value_type = float
    entity = Person
    label = "Connecticut SSP shelter allowance"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CT
    reference = (
        "https://www.ctdssmap.com/CTPortal/Information/Get/UPM#4520.10",
        "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/fact-sheets-and-issue-briefs/fact-sheets/dss-program-standards-chart-effective-010126.pdf",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ct.html",
    )

    def formula(person, period, parameters):
        # Boarding home shelter is understated: real need uses the
        # facility's per diem rate (committee-set, varies by facility),
        # not the $0 in the parameter table.  Modeling the facility
        # rate requires a per-facility input variable.
        p = parameters(period).gov.states.ct.dss.ssp
        arrangement = person("ct_ssp_living_arrangement", period.this_year)
        rent = person("rent", period)
        max_allowance = p.shelter_allowance[arrangement]
        return min_(rent, max_allowance)
