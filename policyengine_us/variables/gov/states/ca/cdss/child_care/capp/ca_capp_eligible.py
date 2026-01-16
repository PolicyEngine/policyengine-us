from policyengine_us.model_api import *


class ca_capp_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for California Alternative Payment Program"
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = (
        "https://cdrv.org/cdr-programs-and-services/california-work-opportunity-and-responsibility-to-kids-calworks-alternative-payment-programs/",
        "https://www.cdss.ca.gov/inforesources/calworks-child-care/subsidized-programs",
    )

    def formula(spm_unit, period, parameters):
        # CAPP is for families who have NEVER received CalWORKs
        ever_received = spm_unit("ever_received_calworks", period.this_year)
        never_received_calworks = ~ever_received

        # Income must be at or below 85% SMI
        income_eligible = spm_unit("ca_child_care_income_eligible", period)

        # Must have a need for child care (work requirement)
        need_eligible = spm_unit(
            "ca_calworks_child_care_meets_work_requirement", period.this_year
        )

        # Must have age-eligible children
        age_eligible = spm_unit("ca_calworks_child_care_age_eligible", period)

        # NOTE: CAPP is subject to funding availability and waitlists,
        # which cannot be modeled in PolicyEngine. We assume enrollment.
        return (
            never_received_calworks
            & income_eligible
            & need_eligible
            & age_eligible
        )
