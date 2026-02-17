from policyengine_us.model_api import *


class ca_meets_snap_abawd_work_requirements(Variable):
    value_type = bool
    entity = Person
    label = "Person meets California pre-HR1 SNAP ABAWD work requirements"
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.24",
        "https://www.cdss.ca.gov/Portals/9/Additional-Resources/Letters-and-Notices/ACLs/2025/25-93.pdf",
    )

    def formula(person, period, parameters):
        # Pre-HR1 federal parameters (before July 2025)
        p = parameters("2025-06-01").gov.usda.snap.work_requirements.abawd
        age = person("monthly_age", period)
        weekly_hours_worked = person(
            "weekly_hours_worked_before_lsr", period.this_year
        )
        is_working = weekly_hours_worked >= p.weekly_hours_threshold
        working_age_exempt = p.age_threshold.exempted.calc(age)
        is_disabled = person("is_disabled", period)
        is_dependent = person("is_tax_unit_dependent", period)
        is_qualifying_child = age < p.age_threshold.dependent
        is_parent = person("is_parent", period)
        has_child = person.spm_unit.any(is_dependent & is_qualifying_child)
        exempt_parent = is_parent & has_child
        meets_general = person("meets_snap_general_work_requirements", period)
        is_pregnant = person("is_pregnant", period)
        is_homeless = person.household("is_homeless", period)
        is_veteran = person("is_veteran", period)
        return (
            is_working
            | working_age_exempt
            | is_disabled
            | exempt_parent
            | meets_general
            | is_pregnant
            | is_homeless
            | is_veteran
        )
