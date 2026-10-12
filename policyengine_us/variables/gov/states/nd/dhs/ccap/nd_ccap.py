from policyengine_us.model_api import *


class nd_ccap(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "North Dakota CCAP benefit amount"
    definition_period = MONTH
    defined_for = "nd_ccap_eligible"
    reference = "https://www.nd.gov/dhs/policymanuals/40028/40028.htm"

    def formula(spm_unit, period, parameters):
        # The benefit is the base subsidy (capped at billed expenses and net of
        # the co-payment) plus the additive QRIS step bonus and infant/toddler
        # bonus. The two bonuses are separate provider payments, so they are
        # not capped at the family's billed expenses and not reduced by the
        # co-payment (400-28-100-30).
        base_subsidy = spm_unit("nd_ccap_base_subsidy", period)
        person = spm_unit.members
        # Reported care days or hours establish participation independently
        # of the missing-hours pricing fallback.
        weekly_hours = person("childcare_hours_per_week", period.this_year)
        daily_hours = person("childcare_hours_per_day", period.this_year)
        monthly_days = person("childcare_attending_days_per_month", period.this_year)
        weekly_days = person("childcare_days_per_week", period.this_year)
        in_care = (
            (weekly_hours > 0)
            | (daily_hours > 0)
            | (monthly_days > 0)
            | (weekly_days > 0)
        )
        qris_step_bonus = spm_unit.sum(
            person("nd_ccap_qris_step_bonus", period) * in_care
        )
        infant_toddler_bonus = spm_unit.sum(
            person("nd_ccap_infant_toddler_bonus", period) * in_care
        )
        return base_subsidy + qris_step_bonus + infant_toddler_bonus
