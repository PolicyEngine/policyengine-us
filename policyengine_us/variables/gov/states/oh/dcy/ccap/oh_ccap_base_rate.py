from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.oh.dcy.ccap.oh_ccap_provider_type import (
    OHCCAPProviderType,
)
from policyengine_us.variables.gov.states.oh.dcy.ccap.oh_ccap_time_category import (
    OHCCAPTimeCategory,
)


class oh_ccap_base_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Ohio CCAP monthly maximum reimbursement rate before add-ons"
    definition_period = MONTH
    defined_for = "oh_ccap_eligible_child"
    reference = "https://codes.ohio.gov/assets/laws/administrative-code/pdfs/5180/6/1/5180$6-1-10_PH_FF_N_APP1_20251020_1028.pdf#page=1"

    def formula(person, period, parameters):
        # 5180:6-1-10 Appendix A: maximum reimbursement ceilings keyed by
        # county rate category, age group, and time category. Hourly cells are
        # per-hour dollar amounts; part-time and full-time cells are weekly
        # dollar amounts.
        p = parameters(period).gov.states.oh.dcy.ccap.rates
        # 5180:6-1-10(B)(1)(a) keys the rate to the provider's county of
        # location; provider location is not tracked, so the household's
        # county serves as a proxy.
        rate_category = person.household(
            "oh_ccap_county_rate_category", period.this_year
        )
        age_group = person("oh_ccap_child_age_group", period)
        time_category = person("oh_ccap_time_category", period)
        provider_type = person("oh_ccap_provider_type", period)

        center_rate = p.center[rate_category][age_group][time_category]
        home_rate = p.home[rate_category][age_group][time_category]
        table_rate = where(
            provider_type == OHCCAPProviderType.CENTER,
            center_rate,
            home_rate,
        )
        # Convert the published rate to a monthly amount. Hourly rates apply to
        # the child's authorized care hours; part-time and full-time rates are
        # weekly amounts converted to monthly.
        weekly_hours = person("childcare_hours_per_week", period.this_year)
        monthly_hours = weekly_hours * WEEKS_IN_YEAR / MONTHS_IN_YEAR
        is_hourly = time_category == OHCCAPTimeCategory.HOURLY
        monthly_rate = where(
            is_hourly,
            table_rate * monthly_hours,
            table_rate * WEEKS_IN_YEAR / MONTHS_IN_YEAR,
        )
        # Do not pay for a child who is not actually in care.
        return where(monthly_hours >= 1, monthly_rate, 0)
