from policyengine_us.model_api import *


class nc_sa(Variable):
    value_type = float
    entity = Person
    label = "North Carolina State and County Special Assistance"
    definition_period = MONTH
    unit = USD
    defined_for = "nc_sa_eligible"
    reference = (
        # PDF pages 207-210
        "https://policies.ncdhhs.gov/wp-content/uploads/Special-Assistance-Manual-Rev-June-2026.pdf#page=207",
        # PDF pages 42-43
        "https://policies.ncdhhs.gov/wp-content/uploads/Special-Assistance-In-Home-Program-Manual-Rev-June-2026.pdf#page=42",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nc.dhhs.sa
        setting = person("nc_sa_care_setting", period)
        settings = setting.possible_values
        enhanced = (setting == settings.SPECIAL_CARE_UNIT) | (
            setting == settings.IN_HOME_ENHANCED
        )
        published_rate = where(enhanced, p.rate.enhanced, p.rate.basic)
        in_home = (setting == settings.IN_HOME) | (setting == settings.IN_HOME_ENHANCED)
        rate = where(
            in_home,
            published_rate,
            min_(max_(person("nc_sa_facility_rate", period), 0), published_rate),
        )
        income = person("nc_sa_countable_income", period)
        full = np.floor(max_(rate + p.personal_needs_allowance - income, 0) + 0.5)
        days = clip(person("nc_sa_days_eligible", period), 0, period.days)
        # For the first partial month, income is not deducted and the full
        # personal-needs allowance is added after prorating the facility rate.
        daily = np.floor(rate.astype(np.float64) / period.days * 100 + 0.5) / 100
        partial = np.floor(daily * days + p.personal_needs_allowance + 0.5)
        return (days > 0) * where(days == period.days, full, partial)
