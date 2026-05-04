from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.mn.dhs.msa.mn_msa_living_arrangement import (
    MNMSALivingArrangement,
)


class mn_msa_housing_assistance_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Minnesota Supplemental Aid housing allowance under § 256D.44 Subd. 5(g)"
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.dhs.state.mn.us/main/idcplg?IdcService=GET_DYNAMIC_CONVERSION&dDocName=cm_002324&RevisionSelectionMethod=LatestReleased",
    )

    def formula(person, period, parameters):
        pathway_eligible = person("mn_msa_housing_assistance_pathway_eligible", period)
        living_arrangement = person("mn_msa_living_arrangement", period)
        LA = MNMSALivingArrangement
        is_couple_arrangement = (living_arrangement == LA.COUPLE_LIVING_ALONE) | (
            living_arrangement == LA.COUPLE_LIVING_WITH_OTHERS
        )

        rent = person("rent", period)
        utility_expense = person.spm_unit("utility_expense", period)
        shelter_cost = where(
            is_couple_arrangement,
            person.marital_unit.sum(rent) + utility_expense,
            rent + utility_expense,
        )

        gross_income = person("mn_msa_gross_income", period)
        assistance_unit_income = where(
            is_couple_arrangement,
            person.marital_unit.sum(gross_income),
            gross_income,
        )
        high_shelter_cost = shelter_cost > 0.4 * assistance_unit_income
        receives_housing_assistance = person.spm_unit(
            "receives_housing_assistance", period
        )

        return pathway_eligible & high_shelter_cost & ~receives_housing_assistance
