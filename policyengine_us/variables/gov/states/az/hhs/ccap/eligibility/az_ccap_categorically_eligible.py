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
        head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        employed = person("weekly_hours_worked", period.this_year) > 0
        # R6-5-4914(A)(1)-(A)(2): Cash Assistance / Jobs participants qualify without
        # regard to income only when they need child care to maintain employment, so
        # we require an employed head/spouse. (Jobs-program participation is folded
        # into Cash Assistance / TANF enrollment, as it is not separately tracked.)
        cash_assistance_for_work = spm_unit("is_tanf_enrolled", period) & spm_unit.any(
            head_or_spouse & employed
        )
        # R6-5-4914(A)(3): DCS/DDD referrals and foster-care families qualify
        # regardless of income or employment.
        protective_services = spm_unit.any(
            person("receives_or_needs_protective_services", period.this_year)
        )
        foster_care = spm_unit.any(person("is_in_foster_care", period))
        return cash_assistance_for_work | protective_services | foster_care
