from policyengine_us.model_api import *


class is_head_start_categorically_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Early Head Start or Head Start program eligible"
    definition_period = YEAR
    reference = (
        "https://headstart.gov/policy/45-cfr-chap-xiii/1302-12-determining-verifying-documenting-eligibility",
        "https://www.law.cornell.edu/cfr/text/45/1302.12",
        "https://www.hhs.gov/answers/programs-for-families-and-children/how-can-i-get-my-child-into-head-start/index.html",
        # ACF IM 22-03 interprets SNAP as qualifying public assistance
        # under 45 CFR 1302.12(c)(1)(ii).
        "https://www.headstart.gov/policy/im/acf-im-hs-22-03",
        "https://www.headstart.gov/ersea/article/snap-public-assistance-head-start-eligibility-faqs",
    )

    def formula(person, period, parameters):
        # Person-level: child's own status (not aggregated across family).
        # 45 CFR 1302.12(c)(1)(iv): "The child is in foster care." This is a
        # current placement, so read is_in_foster_care in each month of the
        # year; a child who has left care (was_in_foster_care) does not
        # qualify on that basis.
        in_foster_care = np.any(
            [
                person("is_in_foster_care", month)
                for month in period.get_subperiods(MONTH)
            ],
            axis=0,
        )
        person_eligible = person.household("is_homeless", period) | in_foster_care

        # Family-level: family eligible for public assistance (aggregated at spm_unit)
        family_eligible = (
            add(person.spm_unit, period, ["tanf", "ssi", "snap"]) > 0
        ) | (
            add(
                person.spm_unit,
                period,
                ["receives_tanf", "receives_ssi", "receives_snap"],
            )
            > 0
        )

        return family_eligible | person_eligible
