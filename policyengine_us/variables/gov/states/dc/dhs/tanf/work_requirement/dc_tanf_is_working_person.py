from policyengine_us.model_api import *


class dc_tanf_is_working_person(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Person is working under DC Temporary Assistance for Needy Families (TANF)"
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.19b#(b)"
    )
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.dc.dhs.tanf.work_requirement.required_hours
        monthly_hours_worked = person("monthly_hours_worked", period)
        age = person("monthly_age", period)
        has_child_under_6 = person.spm_unit.any(
            age < p.single_parent.lower.young_child_age_threshold
        )
        single_parent_requirement = where(
            has_child_under_6,
            monthly_hours_worked >= p.single_parent.lower.amount,
            monthly_hours_worked >= p.single_parent.higher.amount,
        )
        two_parents_requirement = monthly_hours_worked >= p.two_parents.amount
        filing_status = person.tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT

        return where(joint, two_parents_requirement, single_parent_requirement)
