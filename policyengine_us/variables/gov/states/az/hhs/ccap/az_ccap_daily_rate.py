from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.az.hhs.ccap.az_ccap_provider_type import (
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
        p = parameters(period).gov.states.az.hhs.ccap.rates
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
        # CCA-1210B item 14: a disabled child (documented via IFSP/IEP/ISP/504 plan —
        # we use is_disabled as a proxy) at a provider with a 3-5 star Quality First
        # rating or national accreditation (the `quality` gate) receives the flat
        # Special Needs Enhanced Rate, which replaces the base/age/provider rate.
        # We don't model the separate +35% CDA tier for CDA-credentialed certified
        # family / in-home providers at the moment (the +40% quality tier dominates
        # it wherever a provider holds both credentials).
        return where(special_needs & quality, p.special_needs, regular_rate)
