from policyengine_us.model_api import *


class meets_snap_abawd_work_requirements(Variable):  # This one get a reform
    value_type = bool
    entity = Person
    label = "Person is eligible for SNAP benefits via ABAWD work requirements"
    definition_period = MONTH
    reference = "https://www.fns.usda.gov/snap/work-requirements"

    def formula(person, period, parameters):
        p = parameters(period).gov.usda.snap.work_requirements
        age = person("monthly_age", period)
        monthly_hours_worked = person("monthly_hours_worked", period)
        is_dependent = person("is_tax_unit_dependent", period)
        is_child = age < 18  # (reduce to 7 in reform Sec. 10002)
        # https://agriculture.house.gov/uploadedfiles/section_by_section_hac_print_reconciliation_final_700pm.pdf
        no_dependent_child = person.spm_unit.sum(is_dependent & is_child) == 0
        # Too old or too young can exempted from working
        worked_exempted_age = (
            age < 18 | age > 54
        )  # (increase to 64 in reform Sec. 10002)
        # Work at least 80 hours a month
        is_working = monthly_hours_worked >= 80
        # Unable to work due to a physical or mental limitation
        is_disabled = person("is_disabled", period)
        # Pregnant
        is_pregnant = person("is_pregnant", period)
        # Have someone under 18 in your SNAP household (but its not a dependent?)
        # A veteran
        is_veteran = person("is_veteran", period)
        # Homeless
        is_homeless = person.household("is_homeless", period)
        return no_dependent_child & (
            worked_exempted_age
            | is_working
            | is_disabled
            | is_pregnant
            | is_veteran
            | is_homeless
        )
