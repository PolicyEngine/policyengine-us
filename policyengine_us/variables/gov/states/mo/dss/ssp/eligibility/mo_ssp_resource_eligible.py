from policyengine_us.model_api import *


class mo_ssp_resource_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Missouri SSP resource eligible"
    definition_period = MONTH
    defined_for = StateCode.MO
    reference = (
        "https://dssmanuals.mo.gov/supplemental-aid-to-the-blind/0405-000-00/0405-050-00/",
        "https://dssmanuals.mo.gov/wp-content/uploads/2022/07/mhabd-appendix-j.pdf",
        "https://dssmanuals.mo.gov/wp-content/uploads/2018/10/appendix_k.pdf",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/mo.html",
    )

    def formula(person, period, parameters):
        living_arrangement = person("mo_ssp_living_arrangement", period)
        categories = living_arrangement.possible_values
        is_sab = living_arrangement == categories.SAB
        is_snc = (living_arrangement != categories.SAB) & (
            living_arrangement != categories.NONE
        )

        personal_resources = person("ssi_countable_resources", period.this_year)
        married = person.spm_unit("spm_unit_is_married", period.this_year)
        countable_resources = where(
            married,
            person.marital_unit.sum(personal_resources),
            personal_resources,
        )

        p = parameters(period).gov.states.mo.dss.ssp.eligibility.resource_limit
        sab_limit = where(married, p.sab.couple, p.sab.individual)
        snc_limit = where(married, p.snc.couple, p.snc.individual)
        resource_limit = where(is_sab, sab_limit, snc_limit)
        return ~(is_sab | is_snc) | (countable_resources <= resource_limit)
