from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_reconciled_snap_abawd_work_requirement() -> Reform:
    class meets_snap_abawd_work_requirements(Variable):
        value_type = bool
        entity = Person
        label = "Person is eligible for SNAP benefits via Able-Bodied Adult Without Dependents (ABAWD) work requirements"
        definition_period = MONTH
        reference = "https://agriculture.house.gov/uploadedfiles/ag-recon-combo_03_xml.pdf#page=4"

        def formula(person, period, parameters):
            p = parameters(period).gov.usda.snap.work_requirements.abawd
            age = person("monthly_age", period)
            weekly_hours_worked = person(
                "weekly_hours_worked", period.this_year
            )
            # Work at least 20 hours a week
            is_working = weekly_hours_worked >= p.weekly_hours_threshold
            # Under 18 or 65 years of age or older are exempted (baseline is 18 or 65) (A)
            worked_exempted_age = p.age_threshold.exempted.calc(age)
            # Unable to work due to a physical or mental limitation (B)
            is_disabled = person("is_disabled", period)
            # Parent of a household member under 7 (baseline is 18) (C)
            is_dependent = person("is_tax_unit_dependent", period)
            is_qualifying_child = age < p.age_threshold.dependent
            is_parent = person("is_parent", period)
            has_child = person.spm_unit.any(is_dependent & is_qualifying_child)
            exempted_parent = is_parent & has_child
            # Exempted from the general work requirements (D)
            meets_snap_general_work_requirements = person(
                "meets_snap_general_work_requirements", period
            )
            # Pregnant (E)
            is_pregnant = person("is_pregnant", period)
            # Homeless (remove in 2030) (F)
            is_homeless = person.household("is_homeless", period)
            # A veteran (remove in 2030) (G)
            is_veteran = person("is_veteran", period)
            # Responsible for a child 7 or older, and is married to individual who is working (I)
            is_child = person("is_child", period)
            older_child_dependent = (
                is_dependent & is_child & ~is_qualifying_child
            )
            is_married = person.family("is_married", period)
            has_older_child_dependent = person.spm_unit.any(
                older_child_dependent
            )
            is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
            has_head_or_spouse_working = person.spm_unit.any(
                is_head_or_spouse & is_working
            )
            exempted_married_person = where(
                is_married & has_older_child_dependent,
                has_head_or_spouse_working,
                0,
            )
            # Sunset provision effects on 2030-10-01
            p_reform = parameters(
                period
            ).gov.contrib.reconciliation.snap_abawd_work_requirement
            base_conditions = (
                is_working
                | worked_exempted_age
                | is_disabled
                | exempted_parent
                | meets_snap_general_work_requirements
                | is_pregnant
                | exempted_married_person
            )
            if p_reform.sunset_provision_in_effect:
                return base_conditions
            return base_conditions | is_homeless | is_veteran

    def modify_parameters(parameters):
        parameters.gov.usda.snap.work_requirements.abawd.age_threshold.dependent.update(
            start=instant("2027-01-01"), stop=instant("2035-12-31"), value=7
        )
        parameters.gov.usda.snap.work_requirements.abawd.age_threshold.exempted[
            2
        ].threshold.update(
            start=instant("2027-01-01"),
            stop=instant("2035-12-31"),
            value=65,
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
