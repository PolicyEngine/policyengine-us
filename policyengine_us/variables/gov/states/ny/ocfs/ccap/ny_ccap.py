from policyengine_us.model_api import *


class ny_ccap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "New York Child Care Assistance Program benefit"
    unit = USD
    defined_for = StateCode.NY
    reference = (
        "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=39",
        # PDF pages 3, 9-10
        "https://ocfs.ny.gov/main/policies/external/2024/lcm/24-OCFS-LCM-22.pdf#page=3",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        # ny_ccap_eligible_child carries New York's income test as well as the
        # categorical routes that waive it, so no separate income gate is
        # applied here.
        eligible = person("ny_ccap_eligible_child", period)
        in_care = person("childcare_hours_per_day", period.this_year) > 0
        counted = eligible & in_care
        # Each child keeps their expense share, including an ineligible
        # sibling's share. Apply differentials after the actual-cost cap so
        # a qualifying payment can exceed the provider's charge.
        payment = person("ny_ccap_payment_rate", period)
        reimbursable_care = spm_unit.sum(payment * counted)
        # 415.3(e)(5): one family share per family regardless of the number of
        # children receiving care, so it is subtracted once from the total.
        family_share = spm_unit("ny_ccap_family_share", period)
        return max_(reimbursable_care - family_share, 0)
