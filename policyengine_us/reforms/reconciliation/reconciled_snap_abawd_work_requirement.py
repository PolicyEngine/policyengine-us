from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_reconciled_snap_abawd_work_requirement() -> Reform:
    class meets_snap_abawd_work_requirements(
        Variable
    ):  # This one get a reform
        value_type = bool
        entity = Person
        label = "Person is eligible for SNAP benefits via Able-Bodied Adult Without Dependents (ABAWD) work requirements"
        definition_period = MONTH
        reference = "https://www.law.cornell.edu/cfr/text/7/273.24"

        def formula(person, period, parameters):
            p = parameters(period).gov.usda.snap.work_requirements.abawd
            age = person("monthly_age", period)
            weekly_hours_worked = person(
                "weekly_hours_worked_before_lsr", period.this_year
            )
            # Too old or too young can exempted from working
            worked_exempted_age = p.age_threshold.work_exempted.calc(age)
            # Unable to work due to a physical or mental limitation
            is_disabled = person("is_disabled", period)
            # Work at least 20 hours a week
            is_working = weekly_hours_worked >= p.weekly_hours_threshold
            # Pregnant
            is_pregnant = person("is_pregnant", period)
            # Parent of a household member under 18
            is_dependent = person("is_tax_unit_dependent", period)
            is_child = age >= p.age_threshold.dependent
            is_parent = person("is_parent", period)
            has_child = person.spm_unit.any(is_dependent & is_child)
            exempted_parent = is_parent & has_child
            return (
                worked_exempted_age
                | is_working
                | is_disabled
                | is_pregnant
                | exempted_parent
            )

    def modify_parameters(parameters):
        parameters.gov.usda.snap.work_requirements.abawd.age_threshold.dependent.update(
            start=instant("2027-01-01"), stop=instant("2035-12-31"), value=7
        )

        parameters.gov.usda.snap.work_requirements.abawd.age_threshold.work_exempted.update(
            start=instant("2027-01-01"),
            stop=instant("2035-12-31"),
            value=65,  # thresholds[-1]: 65
        )
        return parameters

    class reform(Reform):
        def apply(self):
            self.update_variable(meets_snap_abawd_work_requirements)
            self.modify_parameters(modify_parameters)

    return reform


def create_reconciled_snap_abawd_work_requirement_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_reconciled_snap_abawd_work_requirement()

    p = parameters.gov.contrib.reconciliation.snap_abawd_work_requirement

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_reconciled_snap_abawd_work_requirement()
    else:
        return None


reconciled_snap_abawd_work_requirement = (
    create_reconciled_snap_abawd_work_requirement_reform(
        None, None, bypass=True
    )
)
