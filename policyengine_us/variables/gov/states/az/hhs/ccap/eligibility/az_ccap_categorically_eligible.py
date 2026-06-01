from policyengine_us.model_api import *


class az_ccap_categorically_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Categorically eligible for Arizona Child Care Assistance without regard to income"
    definition_period = MONTH
    defined_for = StateCode.AZ
    reference = (
        # R6-5-4914(A) Child Care Assistance Without Regard to Income
        "https://apps.azsos.gov/public_services/Title_06/6-05.pdf#page=29",
        # R6-5-4915 (no fee/copayment for these families)
        "https://apps.azsos.gov/public_services/Title_06/6-05.pdf#page=33",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        # R6-5-4914(A): Cash Assistance / Jobs participants needing child care for
        # an activity, and families referred by DCS/DDD or in foster care, receive
        # Child Care Assistance without regard to income (and without a copay under
        # R6-5-4915). The "needing child care for an activity" condition is enforced
        # separately by az_ccap_activity_eligible, so we do not re-test employment
        # here. We don't separately track Jobs-program participation at the moment,
        # so it is folded into Cash Assistance (TANF) enrollment.
        tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        protective_services = spm_unit.any(
            person("receives_or_needs_protective_services", period.this_year)
        )
        foster_care = spm_unit.any(person("is_in_foster_care", period))
        return tanf_enrolled | protective_services | foster_care
