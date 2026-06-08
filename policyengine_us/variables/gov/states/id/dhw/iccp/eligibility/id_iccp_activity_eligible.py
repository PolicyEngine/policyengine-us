from policyengine_us.model_api import *


class id_iccp_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Activity eligible for the Idaho Child Care Program"
    defined_for = StateCode.ID
    reference = "https://adminrules.idaho.gov/rules/current/16/160612.pdf#page=13"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        # Employment (IDAPA 16.06.12.200.01) and self-employment (200.02).
        has_employment = (person("employment_income", period) > 0) | (
            add(
                person,
                period,
                ["self_employment_income", "sstb_self_employment_income"],
            )
            > 0
        )
        # Training or education (IDAPA 16.06.12.200.03).
        is_student = person("is_full_time_student", period.this_year)
        individually_eligible = has_employment | is_student
        # Fallback for non-derivable activities (preventive services 200.04,
        # Personal Responsibility Contract 200.05).
        fallback = spm_unit("meets_ccdf_activity_test", period.this_year)
        # IDAPA 16.06.12.200 requires each parent in the household to be
        # engaged in a qualifying activity.
        n_parents = spm_unit.sum(is_head_or_spouse)
        n_qualifying = spm_unit.sum(is_head_or_spouse & individually_eligible)
        all_parents_qualify = n_qualifying >= n_parents
        return all_parents_qualify | fallback
