from policyengine_us.model_api import *


class snap_countable_earner(Variable):
    value_type = bool
    entity = Person
    label = "Countable income earner"
    documentation = "Whether this person's earned income is counted for SNAP"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2014, "
        "https://www.law.cornell.edu/cfr/text/7/273.9#c_3"
    )

    def formula(person, period, parameters):
        # Children in K-12 have income excluded
        is_excluded_child = person("snap_excluded_child_earner", period)

        # Federal Work Study participants have income excluded
        is_work_study_participant = person(
            "is_federal_work_study_participant", period.this_year
        )

        return ~(is_excluded_child | is_work_study_participant)
