from policyengine_us.model_api import *


class mo_ssp_resource_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Missouri SSP resource eligible"
    definition_period = MONTH
    defined_for = StateCode.MO
    reference = (
        "https://dssmanuals.mo.gov/supplemental-aid-to-the-blind/0405-000-00/0405-050-00/",
        "https://dssmanuals.mo.gov/december-1973-eligibility-requirements/1035-000-00/1035-005-00/",
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

        # The couple limit applies to property of either spouse when the
        # claimant is married and living with the spouse (§ 1035.005.00), so
        # the test follows the claimant's marital unit rather than the SPM unit.
        personal_resources = person("ssi_countable_resources", period.this_year)
        countable_resources = person.marital_unit.sum(personal_resources)
        married = person.marital_unit.nb_persons() == 2

        p = parameters(period).gov.states.mo.dss.ssp.eligibility.resource_limit
        sab_limit = where(married, p.sab.couple, p.sab.individual)
        snc_limit = where(married, p.snc.couple, p.snc.individual)
        resource_limit = where(is_sab, sab_limit, snc_limit)
        return ~(is_sab | is_snc) | (countable_resources <= resource_limit)
