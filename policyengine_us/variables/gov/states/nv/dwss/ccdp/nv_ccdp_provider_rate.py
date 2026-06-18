from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.nv.dwss.ccdp.nv_ccdp_provider_type import (
    NVCCDPProviderType,
)


class nv_ccdp_provider_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Nevada CCDP daily provider reimbursement rate"
    definition_period = MONTH
    defined_for = "nv_ccdp_eligible_child"
    reference = "https://www.dss.nv.gov/siteassets/dwss.nv.gov/content/care/ACF-118_CCDF_FFY_2025-2027_For_Nevada__3.pdf#page=54"

    def formula(person, period, parameters):
        # CCDF State Plan Section 4.3.1, Tables 1-2: per-day base reimbursement
        # rate keyed by region x provider type x age group. These are the
        # 1-Star (base) rates; the Policy Manual MS 633.2 QRIS star-level
        # enhancements (stars 2-5) are a conservative floor we don't track at
        # the moment.
        p = parameters(period).gov.states.nv.dwss.ccdp.rates
        provider_type = person("nv_ccdp_provider_type", period)
        region = person("nv_ccdp_region", period)
        age_group = person("nv_ccdp_age_group", period)
        center_rate = p.center[region][age_group]
        fcc_rate = p.fcc[region][age_group]
        return where(
            provider_type == NVCCDPProviderType.FCC,
            fcc_rate,
            center_rate,
        )
