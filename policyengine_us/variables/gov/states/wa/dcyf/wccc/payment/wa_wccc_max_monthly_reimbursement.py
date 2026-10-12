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
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0190",
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0200",
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0205",
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0240",
    )

    def formula(person, period, parameters):
        # We use the FULL_DAY monthly billing unit counts for every day_type
        # at the moment. WAC 110-15-0190(3)(c)/(6)/(8)(b) defines distinct
        # half-day / partial-day unit counts, but we don't track those
        # separately; wa_wccc_day_type defaults to FULL_DAY, so microsim is
        # unaffected. When day-type-specific units are added, also add the
        # corresponding parameters (e.g., center_half_days).
        rates = parameters(period).gov.states.wa.dcyf.wccc.rates
        units = rates.monthly_units
        day_type = person("wa_wccc_day_type", period)

        center_region = person.household("wa_wccc_center_region", period)
        center_age = person("wa_wccc_center_age_group", period)
        center_monthly = (
            rates.center[center_region][center_age][day_type] * units.center_full_days
        )

        family_home_region = person.household("wa_wccc_region", period)
        family_home_age = person("wa_wccc_family_home_age_group", period)
        family_home_monthly = (
            rates.family_home[family_home_region][family_home_age][day_type]
            * units.family_home_full_days
        )

        in_home_monthly = rates.in_home_relative * units.in_home_relative_full_hours

        provider_type = person("wa_wccc_provider_type", period)
        return select(
            [
                provider_type == WAWCCCProviderType.CENTER,
                provider_type == WAWCCCProviderType.FAMILY_HOME,
                provider_type == WAWCCCProviderType.IN_HOME_RELATIVE,
            ],
            [center_monthly, family_home_monthly, in_home_monthly],
        )
