from policyengine_us.model_api import *


class MassachusettsCCFARegion(Enum):
    WESTERN_CENTRAL_AND_SOUTHEAST = "Western, Central & Southeast"
    NORTHEAST = "Northeast"
    METRO_AND_BOSTON_METRO = "Metro & Boston Metro"


class ma_ccfa_region(Variable):
    value_type = Enum
    entity = Household
    possible_values = MassachusettsCCFARegion
    default_value = MassachusettsCCFARegion.WESTERN_CENTRAL_AND_SOUTHEAST
    definition_period = MONTH
    defined_for = StateCode.MA
    label = "Massachusetts Child Care Financial Assistance (CCFA) region"
    reference = "https://www.mass.gov/doc/fiscal-year-2025-child-care-financial-assistance-daily-reimbursement-rates/download"

    def formula(household, period, parameters):
        county = household("county_str", period)

        p = parameters(period).gov.states.ma.eec.ccfa.region
        western_central_and_southeast = np.isin(
            county, p.western_central_and_southeast
        )
        northeast = np.isin(county, p.northeast)
        metro_and_boston_metro = np.isin(county, p.metro_and_boston_metro)

        conditions = [
            western_central_and_southeast,
            northeast,
            metro_and_boston_metro,
        ]
        results = [
            MassachusettsCCFARegion.WESTERN_CENTRAL_AND_SOUTHEAST,
            MassachusettsCCFARegion.NORTHEAST,
            MassachusettsCCFARegion.METRO_AND_BOSTON_METRO,
        ]

        return select(
            conditions,
            results,
            default=MassachusettsCCFARegion.WESTERN_CENTRAL_AND_SOUTHEAST,
        )
