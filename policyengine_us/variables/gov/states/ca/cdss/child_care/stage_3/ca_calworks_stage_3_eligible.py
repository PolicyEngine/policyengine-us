from policyengine_us.model_api import *


class ca_calworks_stage_3_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for California CalWORKs Stage 3 child care"
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=10372.5.&nodeTreePath=16.4.19&lawCode=WIC"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.cdss.child_care.stage_2

        # Must have formerly received CalWORKs
        ever_received = spm_unit("was_calworks_recipient", period.this_year)

        # Not currently receiving CalWORKs cash aid
        currently_receiving = spm_unit("ca_tanf", period) > 0

        # Must have exhausted Stage 2 (more than 24 months since leaving cash aid)
        months_since = spm_unit("months_since_calworks_exit", period)
        exhausted_stage_2 = months_since > p.time_limit_months

        # Former recipient who exhausted Stage 2
        stage_3_recipient = (
            ever_received & ~currently_receiving & exhausted_stage_2
        )

        # Income must be at or below 85% SMI
        income_eligible = spm_unit("ca_child_care_income_eligible", period)

        # Must have a need for child care (work requirement)
        need_eligible = spm_unit(
            "ca_calworks_child_care_meets_work_requirement", period.this_year
        )

        # Must have age-eligible children
        age_eligible = spm_unit("ca_calworks_child_care_age_eligible", period)

        # NOTE: Stage 3 is subject to funding availability, which cannot be
        # modeled in PolicyEngine. We assume funding is available.
        return (
            stage_3_recipient & income_eligible & need_eligible & age_eligible
        )
