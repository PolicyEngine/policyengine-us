from policyengine_us.model_api import *


class VAEAPClimateZone(Enum):
    CENTRAL_MOUNTAIN = "Central Mountain"
    SOUTHWESTERN_MOUNTAIN = "Southwestern Mountain"
    NORTHERN = "Northern"
    WESTERN_PIEDMONT = "Western Piedmont"
    EASTERN_PIEDMONT = "Eastern Piedmont"
    TIDEWATER = "Tidewater"


class va_eap_climate_zone(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = VAEAPClimateZone
    default_value = VAEAPClimateZone.TIDEWATER
    definition_period = YEAR
    label = "Virginia EAP climate zone"
    documentation = "Climate zone of the household's county or independent city under Appendix A. All 133 Virginia localities are assigned; a household without a recognized Virginia county takes the Tidewater default."
    reference = (
        # PDF pages 3-5
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/VA_BenefitMatrix_2026.pdf#page=3",
        # PDF pages 62-64
        "https://www.dss.virginia.gov/media/vdss/benefit-programs/documents/eap/Complete_Manual.pdf#page=62",
        "https://law.lis.virginia.gov/admincodefull/title22/agency40/chapter680/",
    )
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.va.dss.eap.climate_zone
        county = spm_unit.household("county_str", period)
        return select(
            [
                np.isin(county, p.central_mountain),
                np.isin(county, p.southwestern_mountain),
                np.isin(county, p.northern),
                np.isin(county, p.western_piedmont),
                np.isin(county, p.eastern_piedmont),
                np.isin(county, p.tidewater),
            ],
            [
                VAEAPClimateZone.CENTRAL_MOUNTAIN,
                VAEAPClimateZone.SOUTHWESTERN_MOUNTAIN,
                VAEAPClimateZone.NORTHERN,
                VAEAPClimateZone.WESTERN_PIEDMONT,
                VAEAPClimateZone.EASTERN_PIEDMONT,
                VAEAPClimateZone.TIDEWATER,
            ],
            default=VAEAPClimateZone.TIDEWATER,
        )
