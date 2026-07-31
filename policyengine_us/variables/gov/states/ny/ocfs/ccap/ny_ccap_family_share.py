from policyengine_us.model_api import *


class ny_ccap_family_share(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "New York CCAP monthly family share"
    unit = USD
    defined_for = StateCode.NY
    reference = (
        "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=19",
        "https://www.acf.hhs.gov/sites/default/files/documents/occ/NY-Accepted-ACF118-CCDF-FFY-2025-2027-Appendix.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        income = spm_unit("ccdf_income", period)
        fpl = spm_unit("spm_unit_fpg", period)
        income_exceeding_fpl = max_(income - fpl, 0)
        p = parameters(period).gov.states.ny.ocfs.ccap

        if p.statewide_family_share_in_effect:
            calculated_share = income_exceeding_fpl * p.family_share_rate
            minimum_share = p.minimum_weekly_family_share * (
                WEEKS_IN_YEAR / MONTHS_IN_YEAR
            )
            return where(
                income > fpl,
                max_(calculated_share, minimum_share),
                0,
            )

        county = spm_unit.household("county_str", period.this_year)
        historical_rates = p.historical_family_share_rate
        county_names = list(historical_rates._children)
        family_share_rate = select(
            [county == county_name for county_name in county_names],
            [historical_rates[county_name] for county_name in county_names],
            default=0.1,
        )
        minimum_share = p.minimum_weekly_family_share * (WEEKS_IN_YEAR / MONTHS_IN_YEAR)
        return max_(income_exceeding_fpl * family_share_rate, minimum_share)
