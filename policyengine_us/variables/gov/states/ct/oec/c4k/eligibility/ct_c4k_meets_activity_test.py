from policyengine_us.model_api import *


class ct_c4k_meets_activity_test(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    defined_for = StateCode.CT
    label = "Meets Connecticut Care 4 Kids activity test"
    reference = "https://eregulations.ct.gov/eRegsPortal/Browse/RCSA/Title_17bSubtitle_17b-749Section_17b-749-04/"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ct.oec.c4k.age_threshold
        person = spm_unit.members
        # C4K activity test applies to the applicant/caretaker
        # (tax-unit head or spouse) only. A working dependent (e.g., a
        # teen with a summer job) does not satisfy the test for the
        # family.
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        employed = spm_unit.any(
            is_head_or_spouse & (person("employment_income", period) > 0)
        )
        self_employed = spm_unit.any(
            is_head_or_spouse & (person("self_employment_income", period) > 0)
        )
        in_tfa = spm_unit("ct_tfa_eligible", period)
        teen_parent_in_school = spm_unit.any(
            person("is_parent", period.this_year)
            & person("is_in_k12_school", period.this_year)
            & (person("age", period.this_year) < p.teen_parent)
        )
        return employed | self_employed | in_tfa | teen_parent_in_school
