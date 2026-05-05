from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.mo.dss.ssp.mo_ssp_living_arrangement import (
    MOSSPLivingArrangement,
)


class mo_ssp_category_eligible(Variable):
    value_type = bool
    entity = Person
    label = "In a Missouri SSP covered category"
    definition_period = MONTH
    defined_for = StateCode.MO
    reference = (
        "https://revisor.mo.gov/main/OneSection.aspx?section=208.030",
        "https://revisor.mo.gov/main/OneSection.aspx?section=209.040",
    )

    def formula(person, period, parameters):
        living_arrangement = person("mo_ssp_living_arrangement", period)
        categories = living_arrangement.possible_values
        in_snc_facility = (
            (living_arrangement == categories.RCF_LEVEL_I)
            | (living_arrangement == categories.RCF_LEVEL_II_OR_ALF)
            | (living_arrangement == categories.SNF_OR_ICF_NON_MEDICAID)
        )
        is_blind = person("is_blind", period.this_year)
        sab_pathway = (living_arrangement == categories.SAB) & is_blind
        return in_snc_facility | sab_pathway
