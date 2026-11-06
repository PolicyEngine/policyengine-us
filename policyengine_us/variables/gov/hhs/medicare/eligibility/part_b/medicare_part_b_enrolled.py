from policyengine_us.model_api import *


class medicare_part_b_enrolled(Variable):
    value_type = bool
    entity = Person
    label = "Medicare Part B enrolled"
    documentation = (
        "Whether the person is enrolled in Medicare Part B (supplementary "
        "medical insurance). Part B is a separate enrollment from Part A, so "
        "a Medicare enrollee can hold Part A only and owe no Part B premium. "
        "Defaults to true for every Medicare enrollee (medicare_enrolled); "
        "set it to false for a Part A-only enrollee."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1395o#a",
        "https://www.ecfr.gov/current/title-42/section-407.10",
    )

    def formula(person, period, parameters):
        # Every Medicare enrollee is taken to hold Part B unless entered
        # otherwise.
        return person("medicare_enrolled", period)
