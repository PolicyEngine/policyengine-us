from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.mo.dss.ssp.mo_ssp_living_arrangement import (
    MOSSPLivingArrangement,
)


class mo_ssp_age_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets the age threshold for Missouri SSP"
    definition_period = MONTH
    defined_for = StateCode.MO
    reference = (
        "https://revisor.mo.gov/main/OneSection.aspx?section=208.030",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/mo.html",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mo.dss.ssp.age_threshold
        age = person("age", period.this_year)
        living_arrangement = person("mo_ssp_living_arrangement", period)
        is_sab = living_arrangement == MOSSPLivingArrangement.SAB
        threshold = where(is_sab, p.sab, p.snc)
        return age >= threshold
