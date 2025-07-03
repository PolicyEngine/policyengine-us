from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_reconciled_snap_abawd_work_requirement() -> Reform:
    class meets_snap_abawd_work_requirements(Variable):
        value_type = bool
        entity = Person
        label = "Person is eligible for SNAP benefits via Able-Bodied Adult Without Dependents (ABAWD) work requirements"
        definition_period = MONTH
        reference = (
            "https://agriculture.house.gov/uploadedfiles/ag-recon-combo_03_xml.pdf#page=4",
            "https://www.budget.senate.gov/imo/media/doc/the_one_big_beautiful_bill_act.pdf#page=17",
        )

        def formula(person, period, parameters):
            p = parameters(period).gov.usda.snap.work_requirements.abawd
            p_reform = parameters(
                period
            ).gov.contrib.reconciliation.snap_abawd_work_requirement
            age = person("monthly_age", period)
            weekly_hours_worked = person(
                "weekly_hours_worked", period.this_year
            )
            # Work at least 20 hours a week
            is_working = weekly_hours_worked >= p.weekly_hours_threshold
            # Under 18 or 65 years of age or older are exempted (baseline is 18 or 55) (A)
            worked_exempted_age = p.age_threshold.exempted.calc(age)
            # Unable to work due to a physical or mental limitation (B)
            is_disabled = person("is_disabled", period)
            # House version (C) parent of a dependent child under 7 years of age
            # Senate version (C) parent of a dependent child under 14 years of age
            # Current legal code (3) parent of a household member under age 18
            # Don't model this because this contradicts the definition of ABAWD (AWD stands for without dependents)
            # We reflect this dependent age change by updating the parameters
            # Exempt under subsection (d)(2) (D)
            has_incapacitated_person = person.spm_unit.any(
                person("is_incapable_of_self_care", period)
            )
            # Pregnant (E)
            is_pregnant = person("is_pregnant", period)
            # Homeless (remove in 2030) (F)
            is_homeless = person.household("is_homeless", period)
            # A veteran (remove in 2030) (G)
            is_veteran = person("is_veteran", period)
            # Below this section (I), only appears in the House version
            # Responsible for a child 7 or older, and is married to individual who is in compliance
            # with the requirements of paragraph (2) (I)
            # paragraph (2) https://www.govinfo.gov/content/pkg/COMPS-10331/pdf/COMPS-10331.pdf#page=46
            is_dependent = person("is_tax_unit_dependent", period)
            is_qualifying_child = age >= p_reform.house.dependent_age_limit
            is_child = person("is_child", period)
            older_child_dependent = (
                is_dependent & is_child & is_qualifying_child
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
            # House version Sunset provision effects on 2030-10-01
            # Senate version remove homeless and veteran immediately
            base_conditions = (
                is_working
                | worked_exempted_age
                | is_disabled
                | has_incapacitated_person
                | is_pregnant
            )
            if p_reform.house.in_effect:
                if p_reform.house.sunset_provision_in_effect:
                    return base_conditions | exempted_married_person
                return (
                    base_conditions
                    | is_homeless
                    | is_veteran
                    | exempted_married_person
                )
            elif p_reform.senate.in_effect:
                return base_conditions
            else:
                return base_conditions | is_homeless | is_veteran

    class is_snap_dependent_child(Variable):
        value_type = bool
        entity = Person
        label = "Person is a dependent child under SNAP"
        definition_period = MONTH
        reference = "https://www.budget.senate.gov/imo/media/doc/the_one_big_beautiful_bill_act.pdf#page=17"

        def formula(person, period, parameters):
            p = parameters(
                period
            ).gov.usda.snap.work_requirements.abawd.age_threshold
            p_reform = parameters(
                period
            ).gov.contrib.reconciliation.snap_abawd_work_requirement
            age = person("monthly_age", period)
            is_dependent = person("is_tax_unit_dependent", period)
            if p_reform.house.in_effect:
                age_limit = p_reform.house.dependent_age_limit
            elif p_reform.senate.in_effect:
                age_limit = p_reform.senate.dependent_age_limit
            else:
                age_limit = p.dependent
            return is_dependent & (age < age_limit)

    class is_work_exempted_state(Variable):
        value_type = bool
        entity = Household
        label = "State is worked exempted under SNAP"
        definition_period = MONTH
        reference = "https://www.budget.senate.gov/imo/media/doc/the_one_big_beautiful_bill_act.pdf#page=17"

        def formula(household, period, parameters):
            p = parameters(
                period
            ).gov.contrib.reconciliation.snap_abawd_work_requirement
            state_code = household("state_code", period)
            state_code_str = state_code.decode_to_str()
            exempted_state = np.isin(
                state_code_str,
                p.senate.exempted_states,
            )
            if p.senate.in_effect:
                return exempted_state
            return False

    class meets_snap_work_requirements(Variable):
        value_type = bool
        entity = SPMUnit
        label = "SPM Unit is eligible for SNAP benefits via work requirements"
        definition_period = MONTH
        reference = "https://www.fns.usda.gov/snap/work-requirements"

        def formula(spm_unit, period, parameters):
            p = parameters(
                period
            ).gov.contrib.reconciliation.snap_abawd_work_requirement
            person = spm_unit.members
            general_work_requirements = person(
                "meets_snap_general_work_requirements", period
            )
            abawd_work_requirements = person(
                "meets_snap_abawd_work_requirements", period
            )
            # If there is no dependent child, then the SPM unit must meet both work requirements.
            is_dependent_child = person("is_snap_dependent_child", period)
            no_dependent_child = person.spm_unit.sum(is_dependent_child) == 0
            meets_work_requirements_person = where(
                no_dependent_child,
                abawd_work_requirements & general_work_requirements,
                general_work_requirements,
            )
            exempted_state = spm_unit.household(
                "is_work_exempted_state", period
            )
            all_meet_requirements = (
                spm_unit.sum(~meets_work_requirements_person) == 0
            )
            if p.senate.in_effect:
                return all_meet_requirements | exempted_state
            else:
                return all_meet_requirements

    def modify_parameters(parameters):
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
            self.update_variable(is_snap_dependent_child)
            self.update_variable(is_work_exempted_state)
            self.update_variable(meets_snap_work_requirements)
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
        if (
            p(current_period).house.in_effect
            or p(current_period).senate.in_effect
        ):
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
