from policyengine_us.model_api import *


class ky_service_credits_percentage_pre_cutoff(Variable):
    value_type = float
    entity = Person
    label = "Share of service credit months worked before 1998"
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(person, period, parameters):
        pre_cutoff_months = person(
            "ky_service_credit_months_pre_cutoff", period
        )
        post_cutoff_months = person(
            "ky_service_credit_months_post_cutoff", period
        )

        return where(
            pre_cutoff_months + post_cutoff_months > 0,
            pre_cutoff_months / (pre_cutoff_months + post_cutoff_months),
            0,
        )
