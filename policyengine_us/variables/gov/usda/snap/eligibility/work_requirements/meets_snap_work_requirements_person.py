from policyengine_us.model_api import *


class meets_snap_work_requirements_person(Variable):
    value_type = bool
    entity = Person
    label = "Person is eligible for SNAP benefits via work requirements"
    definition_period = MONTH
    reference = (
        "https://www.fns.usda.gov/snap/work-requirements",
        "https://www.law.cornell.edu/cfr/text/7/273.7#f_1",
        "https://www.law.cornell.edu/cfr/text/7/273.24#b",
        "https://www.law.cornell.edu/cfr/text/7/273.24#c_4",
    )

    def formula(person, period, parameters):
        general_work_requirements = person(
            "meets_snap_general_work_requirements", period
        )
        abawd_work_requirements = person("meets_snap_abawd_work_requirements", period)
        # The household-child ABAWD gate (7 CFR 273.24(c)(4); post-HR1
        # threshold from 7 U.S.C. 2015(o)(3)(C)) lives in
        # has_snap_abawd_household_child: a person residing with any
        # household member under the dependent-age threshold is routed
        # around the ABAWD time limit.
        has_household_child = person("has_snap_abawd_household_child", period)
        return where(
            has_household_child,
            general_work_requirements,
            abawd_work_requirements & general_work_requirements,
        )
