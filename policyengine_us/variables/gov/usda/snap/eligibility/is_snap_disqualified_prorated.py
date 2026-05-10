from policyengine_us.model_api import *


class is_snap_disqualified_prorated(Variable):
    value_type = bool
    entity = Person
    label = "SNAP disqualified with prorated treatment"
    documentation = (
        "Whether this person is excluded from the SNAP unit under the "
        "'prorated' treatment of 7 CFR 273.11(c)(2) or (c)(3): the "
        "individual's income is divided evenly among all household "
        "members and only the share that would have gone to eligible "
        "members is counted, while resources continue to count in full. "
        "Applies to members who fail the ABAWD time limit and members "
        "who are not immigration-status eligible."
    )
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.11#c_2",
        "https://www.law.cornell.edu/cfr/text/7/273.11#c_3",
    )

    def formula(person, period, parameters):
        # Dependent child threshold differs: pre-HR1 (18) vs post-HR1 (14).
        hr1_in_effect = person("is_snap_abawd_hr1_in_effect", period)
        p = parameters(period).gov.usda.snap.work_requirements.abawd.age_threshold
        p_pre = parameters(
            "2025-06-01"
        ).gov.usda.snap.work_requirements.abawd.age_threshold
        dep_threshold = where(hr1_in_effect, p.dependent, p_pre.dependent)
        age = person("monthly_age", period)
        is_dependent = person("is_tax_unit_dependent", period)
        is_child = age < dep_threshold
        no_dependent_child = person.spm_unit.sum(is_dependent & is_child) == 0
        abawd_ineligible = (
            no_dependent_child
            & person("meets_snap_general_work_requirements", period)
            & ~person("meets_snap_abawd_work_requirements", period)
        )
        immigration_ineligible = ~person("is_snap_immigration_status_eligible", period)
        return abawd_ineligible | immigration_ineligible
