from policyengine_us.model_api import *


class ca_la_ez_save_eligible(Variable):
    value_type = bool
    entity = Household
    definition_period = MONTH
    label = "Eligible for the Los Angeles County EZ Save program"
    defined_for = "in_la"
    reference = "https://www.ladwp.com/sites/default/files/2023-10/2023_EZ-SAVE_Application_and_Information_05_0.pdf#page=2"

    def formula(household, period, parameters):
        income = household("ca_la_ez_save_countable_income", period)
        fpg = household("ca_la_ez_save_fpg", period)
        p = parameters(period).gov.local.ca.la.dwp.ez_save.eligibility
        income_limit = fpg * p.fpg_limit_increase
        # The applicant must be the customer of record on the LADWP account.
        # tenant_pays_utilities approximates this; the model cannot identify
        # sub-metered tenants, who are not the customer of record.
        pays_utilities = household("tenant_pays_utilities", period.this_year)
        return (income <= income_limit) & pays_utilities
