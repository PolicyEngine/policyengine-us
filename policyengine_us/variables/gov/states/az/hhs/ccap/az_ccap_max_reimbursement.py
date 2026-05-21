from policyengine_us.model_api import *


class az_ccap_max_reimbursement(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Arizona Child Care Assistance Program maximum reimbursement"
    definition_period = MONTH
    defined_for = "az_ccap_eligible_child"
    reference = (
        "https://des.az.gov/sites/default/files/dl/CCA-1227A.pdf#page=1",
        "https://apps.azsos.gov/public_services/Title_06/6-05.pdf#page=39",
    )

    def formula(person, period, parameters):
        daily_rate = person("az_ccap_daily_rate", period)
        attending_days = person("childcare_attending_days_per_month", period.this_year)
        return daily_rate * attending_days
