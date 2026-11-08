from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.co.ccap.rates.co_ccap_provider_type import (
    COCCAPProviderType,
)


class co_ccap_full_time_daily_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = MONTH
    label = "Colorado Child Care Assistance Program full-time daily rate for the child's provider"
    defined_for = StateCode.CO
    reference = (
        # 8 CCR 1403-1 3.130, PDF pages 118 and 119: state-established
        # licensed rates by age band, provider type and quality level, and
        # county rates for qualified exempt providers.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=118",
        "https://drive.google.com/file/d/1wK5dCjkW_uqj06tTd0af9-fC6gAfGu5v/view",
        "https://drive.google.com/drive/folders/1YSLL5Sn32NyKbp8Z0063ldFbAhQwfHW_",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.co.ccap.rates
        county = person.household("county_str", period.this_year)
        # A county outside Colorado's list, such as one the household doesn't
        # report, reads Denver's rates, as co_ccap_fpg_eligible does.
        colorado_counties = np.array(list(p.qualified_exempt._children))
        county = np.where(
            np.isin(county, colorado_counties), county, "DENVER_COUNTY_CO"
        )
        tier = person("co_ccap_quality_tier", period)
        center = p.licensed_center[county][person("co_ccap_center_age_band", period)][
            tier
        ]
        home = p.licensed_home[county][person("co_ccap_home_age_band", period)][tier]
        qualified_exempt = p.qualified_exempt[county][
            person("co_ccap_qualified_exempt_age_band", period)
        ]
        provider_type = person("co_ccap_provider_type", period)
        return select(
            [
                provider_type == COCCAPProviderType.LICENSED_CENTER,
                provider_type == COCCAPProviderType.LICENSED_HOME,
            ],
            [center, home],
            default=qualified_exempt,
        )
