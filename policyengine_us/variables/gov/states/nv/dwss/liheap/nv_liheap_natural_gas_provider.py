from policyengine_us.model_api import *


class NVLIHEAPNaturalGasProvider(Enum):
    # The natural gas company named on the bill. Appendix A of the Energy
    # Assistance Program Manual lists one Southwest Gas deduction for
    # single-family service and for multi-family service in northern Nevada,
    # and a lower one for multi-family service in southern Nevada.
    SOUTHWEST_GAS = "Southwest Gas (single-family, or multi-family in northern Nevada)"
    SOUTHWEST_GAS_SOUTH_MULTI_FAMILY = "Southwest Gas (multi-family in southern Nevada)"
    # NV Energy (Sierra Pacific gas) reports usage only, which Appendix A
    # prices with unit charges, so it has no dollar deduction.
    NV_ENERGY = "NV Energy"
    # A reported company outside the listed choices, or a company that was
    # not reported. Nothing is deducted for either.
    OTHER = "Other natural gas provider"
    UNSPECIFIED = "Unspecified"


class nv_liheap_natural_gas_provider(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = NVLIHEAPNaturalGasProvider
    default_value = NVLIHEAPNaturalGasProvider.UNSPECIFIED
    definition_period = YEAR
    label = "Nevada LIHEAP natural gas provider"
    defined_for = StateCode.NV
    reference = (
        "https://dss.nv.gov/uploadedFiles/dwssnvgov/content/Energy/FY%202026%20EAP%20Manual%2008.2025%20ADA.pdf#page=112",
        "https://www.dss.nv.gov/contentassets/b3bcdb93ea2d4b3f8dc252451a34cbe4/2027-eap-state-manual--08.25.26-1.pdf#page=112",
    )
