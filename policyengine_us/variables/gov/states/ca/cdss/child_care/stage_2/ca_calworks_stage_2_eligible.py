from policyengine_us.model_api import *


class ca_calworks_stage_2_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for California CalWORKs Stage 2 child care"
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = (
        "https://www.law.cornell.edu/regulations/california/5-CCR-18400",
        "https://www.cdss.ca.gov/inforesources/calworks-child-care/program-eligibility",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.cdss.child_care.stage_2

        # Must have formerly received CalWORKs
        ever_received = spm_unit("ever_received_calworks", period.this_year)

        # Not currently receiving CalWORKs cash aid
        currently_receiving = spm_unit("ca_tanf", period) > 0

        # Must be within 24 months of leaving cash aid
        months_since = spm_unit("months_since_calworks_cash_aid", period)
        within_time_limit = months_since <= p.time_limit_months

        # Must be off cash aid but within time limit
        former_recipient = (
            ever_received & ~currently_receiving & within_time_limit
        )

        # Income must be at or below 85% SMI
        income_eligible = spm_unit("ca_child_care_income_eligible", period)

        # Must have a need for child care (work requirement)
        need_eligible = spm_unit(
            "ca_calworks_child_care_meets_work_requirement", period.this_year
        )

        # Must have age-eligible children
        age_eligible = spm_unit("ca_calworks_child_care_age_eligible", period)

        return (
            former_recipient & income_eligible & need_eligible & age_eligible
        )
