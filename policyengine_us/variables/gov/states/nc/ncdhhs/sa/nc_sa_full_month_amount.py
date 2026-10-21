from policyengine_us.model_api import *


class nc_sa_full_month_amount(Variable):
    value_type = float
    entity = Person
    label = "North Carolina SA full-month amount"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.NC
    reference = (
        # PDF pages 207, 209
        "https://policies.ncdhhs.gov/wp-content/uploads/Special-Assistance-Manual-Rev-June-2026.pdf#page=207",
        # PDF pages 41-42
        "https://policies.ncdhhs.gov/wp-content/uploads/Special-Assistance-In-Home-Program-Manual-Rev-June-2026.pdf#page=41",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nc.ncdhhs.sa
        maintenance = person("nc_sa_rate", period) + p.personal_needs_allowance
        income = person("nc_sa_countable_income", period)
        # The maintenance amount less TCMI, rounded to the nearest dollar with
        # $0.50 rounding up (SA-3220 III.A). Work in whole cents so that
        # annual-to-month arithmetic cannot move a value across the half dollar.
        maintenance_cents = np.floor(maintenance.astype(np.float64) * 100 + 0.5)
        income_cents = np.floor(income.astype(np.float64) * 100 + 0.5)
        return max_(np.floor((maintenance_cents - income_cents) / 100 + 0.5), 0)
