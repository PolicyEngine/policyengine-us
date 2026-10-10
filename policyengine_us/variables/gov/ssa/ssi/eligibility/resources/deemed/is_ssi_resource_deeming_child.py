from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_spouse_index,
)


class is_ssi_resource_deeming_child(Variable):
    value_type = bool
    entity = Person
    label = "Child subject to parental SSI resource deeming"
    definition_period = MONTH
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1202#p-416.1202(b)",
        "https://www.ecfr.gov/current/title-20/section-416.1856",
        "https://www.ecfr.gov/current/title-20/section-416.1167",
        "https://secure.ssa.gov/poms.nsf/lnx/0501330200",
    )

    def formula(person, period, parameters):
        # SI 01330.200 B divides only among SSI-eligible children. Match
        # is_ssi_eligible's immigration gate without reading eligibility or
        # the resource test, which depend on this allocation.
        immigration_status = person("immigration_status", period)
        is_citizen = immigration_status == immigration_status.possible_values.CITIZEN
        meets_immigration_status = is_citizen | person(
            "is_ssi_qualified_noncitizen", period
        )
        # 416.1856: 'You are not married' and 'not the head of a household'.
        # Marriage uses the same spouse test as resource deeming, so the
        # default marital unit of a situation that omits marital units does
        # not marry a child to the parent who claims them.
        # age is annual in the model: supply the relevant attained age.
        # A child whose own countable income (including income deemed from
        # parents) already reaches the payment is ineligible 'for any reason'
        # and does not share the excess. Neither reads the resource test.
        income_eligible = person(
            "ssi_countable_income", period.this_year
        ) / MONTHS_IN_YEAR < person("ssi_amount_if_eligible", period)
        return (
            person("is_ssi_aged_blind_disabled", period)
            & meets_immigration_status
            & income_eligible
            & (person("age", period.this_year) < 18)
            & (_ssi_spouse_index(person, period) < 0)
            & ~person("is_household_head", period)
            & ~person("ssi_lives_in_medical_treatment_facility", period)
            & ~person("ssi_resource_deeming_waiver", period)
            & ~person("ssi_resource_deeming_child_is_ineligible", period)
        )
