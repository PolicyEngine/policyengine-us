from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.mi.mdhhs.ccap.mi_ccap_provider_type import (
    MICCAPProviderType,
)


class mi_ccap_block_payment(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Michigan CDC reimbursement per child per two-week pay period"
    definition_period = MONTH
    defined_for = "mi_ccap_eligible_child"
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/706.pdf#page=9",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/706.pdf#page=11",
    )

    def formula(person, period, parameters):
        # BEM 706: licensed centers and group and family homes are reimbursed
        # on a block schedule (billing 1-30 hours pays 30, 31-60 pays 60, 61+
        # pays 90), capped at the child's authorized hours. License-exempt
        # related and unrelated providers are paid hourly with no block, also
        # capped at authorized hours. We don't track hours billed separately
        # from authorized hours at the moment, so billed hours equal the
        # child's authorized tier.
        p = parameters(period).gov.states.mi.mdhhs.ccap
        hourly_rate = person("mi_ccap_hourly_rate", period)
        authorized_hours = person.spm_unit("mi_ccap_authorized_hours", period)
        provider_type = person("mi_ccap_provider_type", period)

        block_hours = p.block_hours.tiers.calc(authorized_hours)
        paid_block_hours = min_(block_hours, authorized_hours)
        block_pay = hourly_rate * paid_block_hours
        # License-exempt: hourly, no block schedule.
        exempt_pay = hourly_rate * authorized_hours

        return where(
            provider_type == MICCAPProviderType.LICENSE_EXEMPT,
            exempt_pay,
            block_pay,
        )
