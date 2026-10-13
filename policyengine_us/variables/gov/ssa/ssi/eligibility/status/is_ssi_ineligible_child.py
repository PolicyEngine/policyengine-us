from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_spouse_index,
)


class is_ssi_ineligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Is an SSI-ineligible child"
    documentation = (
        "A child under the SSI definition who is not eligible for SSI. "
        "Whose child the person is, and whether they live with the "
        "claimant, are tested where the allocation is summed."
    )
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1160#p-416.1160(d)",
        "https://www.ecfr.gov/current/title-20/section-416.1856",
        "https://www.law.cornell.edu/uscode/text/42/1382c#c",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.ssa.ssi.eligibility.child
        # 416.1160(d) takes 'child' from 416.1101, which points to 416.1856:
        # under 18, or under 22 and a student regularly attending school;
        # not married; and not the head of a household. Full-time students
        # stand in for students regularly attending school, as in the
        # blind or disabled working student exclusion.
        student = person("is_full_time_student", period) & (
            person("age", period) < p.student_age_limit
        )
        # Marriage uses the spouse test of SSI resource deeming, so the
        # default marital unit of a situation without marital units does not
        # marry a child to the parent who claims them.
        child = (
            (person("is_child", period) | student)
            & (_ssi_spouse_index(person, period) < 0)
            & ~person("is_household_head", period)
        )
        # 'Is not eligible for SSI benefits': aged, blind or disabled people
        # who meet the citizenship or qualified-noncitizen condition are
        # treated as eligible. The income and resource tests are not read,
        # because they depend on deemed income and so on this allocation.
        immigration_status = person("immigration_status", period)
        is_citizen = immigration_status == immigration_status.possible_values.CITIZEN
        eligible = person("is_ssi_aged_blind_disabled", period) & (
            is_citizen | person("is_ssi_qualified_noncitizen", period)
        )
        return child & ~eligible
