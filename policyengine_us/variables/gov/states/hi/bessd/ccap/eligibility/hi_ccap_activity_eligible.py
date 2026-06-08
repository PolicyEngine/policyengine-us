from policyengine_us.model_api import *


class hi_ccap_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Hawaii CCAP based on caretaker activity"
    definition_period = MONTH
    defined_for = StateCode.HI
    reference = "https://humanservices.hawaii.gov/bessd/files/2013/01/HAR-17-798.2-Child-Care-Services-Rules.pdf#page=15"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        # Approved activities (HAR 17-798.2-9(b)(2)). We model the core
        # work, education/training, and disability/protective-services
        # pathways. Activity pathways for short-term job offers, employment
        # breaks, job search, first-to-work, and protective-order day care
        # rely on timing windows we don't track at the moment.
        is_employed = (person("weekly_hours_worked", period.this_year) > 0) | (
            person("employment_income", period.this_year) > 0
        )
        is_student = person("is_full_time_student", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        protective_services = person(
            "receives_or_needs_protective_services", period.this_year
        )
        individually_eligible = (
            is_employed | is_student | is_disabled | protective_services
        )
        # In a two-parent family, BOTH caretakers must be in an approved
        # activity (HAR 17-798.2-9(b)(2)).
        return spm_unit.sum(is_head_or_spouse & ~individually_eligible) == 0
