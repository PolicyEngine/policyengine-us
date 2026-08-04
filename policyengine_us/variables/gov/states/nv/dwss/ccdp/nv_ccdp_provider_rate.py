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
    reference = "https://www.dss.nv.gov/siteassets/dwss.nv.gov/content/care/Child_Care_Manual_July_2024.pdf#page=107"

    def formula(person, period, parameters):
        # Policy Manual MS 633.2 Licensed Provider Daily Rates: per-day
        # reimbursement rate keyed by region x provider type x age group x
        # Nevada Silver State Stars QRIS tier. The star rating defaults to
        # STAR_1 (the base rate), so a household with no provider star rating
        # supplied falls back to the conservative floor.
        p = parameters(period).gov.states.nv.dwss.ccdp.rates
        provider_type = person("nv_ccdp_provider_type", period)
        region = person("nv_ccdp_region", period)
        age_group = person("nv_ccdp_age_group", period)
        star = person("nv_ccdp_provider_star_rating", period)
        center_rate = p.center[region][age_group][star]
        fcc_rate = p.fcc[region][age_group][star]
        return where(
            provider_type == NVCCDPProviderType.FCC,
            fcc_rate,
            center_rate,
        )
