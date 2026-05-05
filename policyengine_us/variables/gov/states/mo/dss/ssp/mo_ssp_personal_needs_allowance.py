from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.mo.dss.ssp.mo_ssp_living_arrangement import (
    MOSSPLivingArrangement,
)


class mo_ssp_personal_needs_allowance(Variable):
    value_type = float
    entity = Person
    label = "Missouri SSP Personal Needs Allowance"
    unit = USD
    definition_period = MONTH
    defined_for = "mo_ssp_eligible"
    reference = (
        "https://revisor.mo.gov/main/OneSection.aspx?section=208.030",
        "https://dssmanuals.mo.gov/wp-content/uploads/2022/07/mhabd-appendix-j.pdf#page=4",
    )

    def formula(person, period, parameters):
        # RSMo 208.030.5 excludes the PNA when the recipient is already
        # receiving a personal needs allowance from another state or federal
        # program; we don't track that intake at the moment.
        p = parameters(period).gov.states.mo.dss.ssp.snc
        living_arrangement = person("mo_ssp_living_arrangement", period)
        in_snf = living_arrangement == MOSSPLivingArrangement.SNF_OR_ICF_NON_MEDICAID
        return in_snf * p.personal_needs_allowance
