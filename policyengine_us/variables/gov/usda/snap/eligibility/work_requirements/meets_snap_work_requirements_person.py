from policyengine_us.model_api import *


class meets_snap_work_requirements_person(Variable):
    value_type = bool
    entity = Person
    label = "Person is eligible for SNAP benefits via work requirements"
    definition_period = MONTH
    reference = "https://www.fns.usda.gov/snap/work-requirements"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.usda.snap.work_requirements.abawd.age_threshold
        general_work_requirements = person(
            "meets_snap_general_work_requirements", period
        )
        abawd_work_requirements = person(
            "meets_snap_abawd_work_requirements", period
        )
        # If there is no dependent child, then the SPM unit must meet both work requirements.
        age = person("monthly_age", period)
        is_dependent = person("is_tax_unit_dependent", period)
        is_child = age < p.dependent
        no_dependent_child = person.spm_unit.sum(is_dependent & is_child) == 0
        return where(
            no_dependent_child,
            abawd_work_requirements & general_work_requirements,
            general_work_requirements,
        )
