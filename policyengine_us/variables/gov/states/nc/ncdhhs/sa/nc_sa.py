from policyengine_us.model_api import *


class nc_sa(Variable):
    value_type = float
    entity = Person
    label = "North Carolina State-County Special Assistance"
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
        p = parameters(period).gov.states.nc.ncdhhs.sa
        days = person("nc_sa_partial_month_days", period)
        partial_month = (days > 0) & (days < period.days)
        # For the first partial month, income is not deducted and the full
        # personal-needs allowance is added after prorating the rate
        # (SA-3220 IV.A).
        # Work in whole cents so that a per diem or total ending in exactly
        # half a cent or half a dollar rounds up.
        rate = person("nc_sa_rate", period)
        rate_cents = np.floor(rate.astype(np.float64) * 100 + 0.5)
        daily_cents = np.floor(rate_cents / period.days + 0.5)
        allowance_cents = np.floor(p.personal_needs_allowance * 100 + 0.5)
        partial = np.floor((daily_cents * days + allowance_cents) / 100 + 0.5)
        return where(partial_month, partial, person("nc_sa_full_month_amount", period))
