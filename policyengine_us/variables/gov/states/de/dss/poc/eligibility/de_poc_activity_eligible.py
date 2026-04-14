from policyengine_us.model_api import *


class de_poc_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Delaware Purchase of Care based on activity requirements"
    definition_period = MONTH
    defined_for = StateCode.DE
    reference = "https://regulations.delaware.gov/AdminCode/title16/Department%20of%20Health%20and%20Social%20Services/Division%20of%20Social%20Services/11003.shtml"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        # Employment (DSSM 11003)
        has_employment = (person("employment_income", period) > 0) | (
            person("self_employment_income", period) > 0
        )
        # Education / training (DSSM 11003)
        is_student = person("is_full_time_student", period.this_year)
        individually_eligible = has_employment | is_student
        # Fallback for non-derivable activities (E&T, job search,
        # DFS protective referrals, transitional work, homelessness, etc.)
        fallback = spm_unit("meets_ccdf_activity_test", period.this_year)
        # Delaware requires ALL parents to have a qualifying activity
        # in two-parent households (DSSM 11003.6).
        n_parents = spm_unit.sum(is_head_or_spouse)
        n_qualifying = spm_unit.sum(is_head_or_spouse & individually_eligible)
        all_parents_qualify = n_qualifying >= n_parents
        return all_parents_qualify | fallback
