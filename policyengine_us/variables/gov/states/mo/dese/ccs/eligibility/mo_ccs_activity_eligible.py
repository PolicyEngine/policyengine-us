from policyengine_us.model_api import *


class mo_ccs_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Missouri Child Care Subsidy based on need for care"
    definition_period = MONTH
    defined_for = StateCode.MO
    reference = "https://www.law.cornell.edu/regulations/missouri/5-CSR-25-200-060"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        # The need for care is met by employment, training or education, or job
        # search. We don't track activity-hours verification at the moment, so
        # an applicant is treated as meeting the need when an activity is
        # present (Manual secs. 6.1-6.3). Job search (Manual sec. 6.4) is
        # also a qualifying need but has no clean PolicyEngine input, so a
        # family needing care solely for job search is not captured. The
        # incapacitated-parent pathway (Manual sec. 6.5) requires a physician's
        # statement attesting that child care is needed because of the
        # incapacity; we don't track that attestation at the moment, so
        # is_disabled is used as a proxy for the incapacitated parent.
        is_working = person("weekly_hours_worked", period.this_year) > 0
        is_student = person("is_full_time_student", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        individually_eligible = is_working | is_student | is_disabled
        # Require at least one head/spouse, and require every head/spouse to
        # have a qualifying activity so an SPM unit of only dependents does not
        # vacuously pass.
        has_head_or_spouse = spm_unit.sum(is_head_or_spouse) >= 1
        all_covered = spm_unit.sum(is_head_or_spouse & ~individually_eligible) == 0
        # Homelessness is a valid need for care for the whole family (Manual
        # sec. 6.8), so it satisfies the need-for-care requirement on its own
        # — but, unlike the (7)(A) protective categories, a homeless family must
        # still pass the income test.
        is_homeless = spm_unit.household("is_homeless", period.this_year)
        return has_head_or_spouse & (all_covered | is_homeless)
