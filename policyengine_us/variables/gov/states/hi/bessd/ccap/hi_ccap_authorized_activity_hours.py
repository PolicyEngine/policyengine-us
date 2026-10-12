from policyengine_us.model_api import *


class hi_ccap_authorized_activity_hours(Variable):
    value_type = float
    entity = SPMUnit
    unit = "hour"
    label = "Hawaii CCAP authorized monthly activity hours"
    definition_period = MONTH
    defined_for = StateCode.HI
    reference = "https://humanservices.hawaii.gov/bessd/files/2013/01/HAR-17-798.2-Child-Care-Services-Rules.pdf#page=29"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        # HAR 17-798.2-14(b)(1): the child care allowance uses the lesser of the
        # caretaker's activity hours and the child care hours needed. Employed
        # caretakers cap the tier by their work hours; non-work activities
        # (school, disability, protective services) have no tracked hour count,
        # so they are non-binding (np.inf). For two-parent units the binding
        # constraint is the caretaker with the fewest hours, analogous to NH
        # CCAP He-C 6910.07(p). Use the pre-labor-supply-response hours to avoid
        # a circular dependency with behavioral responses.
        weekly_hours = person("weekly_hours_worked_before_lsr", period.this_year)
        is_employed = weekly_hours > 0
        caretaker_weekly_hours = where(is_employed, weekly_hours, np.inf)
        binding_weekly_hours = spm_unit.min(
            where(is_head_or_spouse, caretaker_weekly_hours, np.inf)
        )
        return binding_weekly_hours * (WEEKS_IN_YEAR / MONTHS_IN_YEAR)
