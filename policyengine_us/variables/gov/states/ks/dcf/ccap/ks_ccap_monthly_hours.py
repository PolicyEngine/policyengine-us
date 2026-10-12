from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ks.dcf.ccap.ks_ccap_provider_type import (
    KSCCAPProviderType,
)


class ks_ccap_monthly_hours(Variable):
    value_type = float
    entity = Person
    unit = "hour"
    label = "Kansas CCAP authorized monthly child care hours"
    definition_period = MONTH
    defined_for = "ks_ccap_eligible_child"
    reference = "https://content.dcf.ks.gov/ees/keesm/Current/keesm7600.htm"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ks.dcf.ccap.hours
        weekly_hours = person("childcare_hours_per_week", period.this_year)
        monthly_hours = weekly_hours * WEEKS_IN_YEAR / MONTHS_IN_YEAR
        # Relative providers (in-home and out-of-home) face a lower monthly cap.
        provider_type = person("ks_ccap_provider_type", period)
        types = KSCCAPProviderType
        is_relative = (provider_type == types.IN_HOME_RELATIVE) | (
            provider_type == types.OUT_OF_HOME_RELATIVE
        )
        cap = where(is_relative, p.relative_max_monthly, p.standard_max_monthly)
        return min_(monthly_hours, cap)
