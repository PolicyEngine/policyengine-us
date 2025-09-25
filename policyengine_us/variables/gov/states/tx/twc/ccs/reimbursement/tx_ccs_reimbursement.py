from policyengine_us.model_api import *


class tx_ccs_reimbursement(Variable):
    value_type = float
    entity = Person
    label = "Texas Child Care Services (CCS) reimbursement amount"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.TX
    reference = "https://www.twc.texas.gov/sites/default/files/ccel/docs/bcy25-board-max-provider-payment-rates-4-age-groups-twc.pdf"

    def formula(person, period, parameters):
        # Check if eligible for CCS
        eligible = person("tx_ccs_eligible_child", period)

        # Get the reimbursement parameters for Dallas County
        p = parameters(
            period
        ).gov.states.tx.twc.ccs.reimbursement.dallas_county.rates

        # Get the provider characteristics
        provider_type = person("tx_ccs_provider_type", period)
        provider_rating = person("tx_ccs_provider_rating", period)
        age_category = person("tx_ccs_child_age_category", period)
        care_schedule = person("tx_ccs_care_schedule", period)

        # Look up the rate based on all four characteristics
        # This uses the breakdown structure to access the nested parameters
        rate = p[provider_type][provider_rating][age_category][care_schedule]

        # Calculate monthly reimbursement (rate is per day, using 10 days for easier checking)
        attending_days_per_month = person(
            "childcare_attending_days_per_month", period.this_year
        )
        monthly_reimbursement = rate * attending_days_per_month

        return where(eligible, monthly_reimbursement, 0)
