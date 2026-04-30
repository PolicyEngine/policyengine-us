from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.wa.dcyf.wccc.payment.wa_wccc_provider_type import (
    WAWCCCProviderType,
)


class wa_wccc_max_monthly_reimbursement(Variable):
    value_type = float
    entity = Person
    label = "Washington WCCC maximum monthly reimbursement per child"
    unit = USD
    definition_period = MONTH
    defined_for = "wa_wccc_eligible_child"
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0190"

    def formula(person, period, parameters):
        units = parameters(period).gov.states.wa.dcyf.wccc.rates.monthly_units
        center_monthly = (
            person("wa_wccc_center_daily_rate", period) * units.center_full_days
        )
        family_home_monthly = (
            person("wa_wccc_family_home_daily_rate", period)
            * units.family_home_full_days
        )
        in_home_monthly = (
            person("wa_wccc_in_home_relative_hourly_rate", period)
            * units.in_home_relative_full_hours
        )
        provider_type = person("wa_wccc_provider_type", period)
        return select(
            [
                provider_type == WAWCCCProviderType.CENTER,
                provider_type == WAWCCCProviderType.FAMILY_HOME,
                provider_type == WAWCCCProviderType.IN_HOME_RELATIVE,
            ],
            [center_monthly, family_home_monthly, in_home_monthly],
            default=center_monthly,
        )
