from policyengine_us.model_api import *


class NVLIHEAPElectricityProvider(Enum):
    # The electric company named on the bill. Appendix A of the Energy
    # Assistance Program Manual lists an annual service fee deduction for
    # each company below except NV Energy.
    ALAMO_POWER_DISTRICT = "Alamo Power District"
    BOULDER_CITY = "Boulder City"
    CALIENTE_PUBLIC_UTILITY = "Caliente Public Utility"
    CITY_OF_FALLON = "City of Fallon"
    HARNEY_ELECTRIC = "Harney Electric"
    LINCOLN_COUNTY_POWER = "Lincoln County Power"
    MT_WHEELER_POWER = "Mt. Wheeler Power"
    OVERTON_POWER = "Overton Power"
    RAFT_RIVER_ELECTRIC = "Raft River Electric"
    VALLEY_ELECTRIC = "Valley Electric"
    WELLS_RURAL_ELECTRIC = "Wells Rural Electric"
    # NV Energy (Nevada Power and Sierra Pacific) reports usage only, which
    # Appendix A prices with unit charges, so it has no dollar deduction.
    NV_ENERGY = "NV Energy"
    # A reported company outside the listed choices, or a company that was
    # not reported. Nothing is deducted for either.
    OTHER = "Other electricity provider"
    UNSPECIFIED = "Unspecified"


class nv_liheap_electricity_provider(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = NVLIHEAPElectricityProvider
    default_value = NVLIHEAPElectricityProvider.UNSPECIFIED
    definition_period = YEAR
    label = "Nevada LIHEAP electricity provider"
    defined_for = StateCode.NV
    reference = (
        "https://dss.nv.gov/uploadedFiles/dwssnvgov/content/Energy/FY%202026%20EAP%20Manual%2008.2025%20ADA.pdf#page=112",
        "https://www.dss.nv.gov/contentassets/b3bcdb93ea2d4b3f8dc252451a34cbe4/2027-eap-state-manual--08.25.26-1.pdf#page=112",
    )
