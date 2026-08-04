from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.az.hhs.ccap.reimbursement.az_ccap_provider_type import (
    AZCCAPProviderType,
)


class az_ccap_daily_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Arizona Child Care Assistance Program daily reimbursement rate"
    definition_period = MONTH
    defined_for = "az_ccap_eligible_child"
    reference = (
        "https://des.az.gov/sites/default/files/dl/CCA-1227A.pdf",
        "https://des.az.gov/services/child-and-family/child-care/des-contracted-child-care-provider-resources",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.az.hhs.ccap.reimbursement.rates
        provider_type = person("az_ccap_provider_type", period)
        age_group = person("az_ccap_age_group", period)
        quality = person("az_ccap_quality_enhanced_provider", period)
        special_needs = person("az_ccap_special_needs_child", period)
        base_rate = select(
            [
                provider_type == AZCCAPProviderType.CENTER,
                provider_type == AZCCAPProviderType.GROUP_HOME,
                provider_type == AZCCAPProviderType.CERTIFIED_FAMILY,
                provider_type == AZCCAPProviderType.RELATIVE,
            ],
            [
                p.center[age_group],
                p.group_home[age_group],
                p.certified_family[age_group],
                p.relative[age_group],
            ],
            default=p.center[age_group],
        )
        quality_rate = where(
            provider_type == AZCCAPProviderType.RELATIVE,
            base_rate,
            base_rate * p.quality_multiplier,
        )
        regular_rate = where(quality, quality_rate, base_rate)
        # CCA-1210B item 14 (file page 14): the Special Needs Enhanced Rate is paid
        # only by licensed Child Care Centers and certified Group Homes that hold a
        # 3-5 star Quality First rating or national accreditation (the `quality` gate),
        # for a child with a documented disability (IFSP/IEP/ISP/504 — proxied by
        # az_ccap_special_needs_child). It replaces the base/age/provider rate. We do
        # not model criterion (c)'s "no more than 10% of a group" cap, nor the separate
        # +35% CDA tier for CDA-credentialed certified family / in-home providers.
        is_center_or_group_home = (provider_type == AZCCAPProviderType.CENTER) | (
            provider_type == AZCCAPProviderType.GROUP_HOME
        )
        return where(
            special_needs & quality & is_center_or_group_home,
            p.special_needs,
            regular_rate,
        )
