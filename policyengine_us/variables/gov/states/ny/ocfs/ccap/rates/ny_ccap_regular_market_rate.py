from policyengine_us.model_api import *
from policyengine_us.tools.ny_ccap import ny_ccap_monthly_rate


class ny_ccap_regular_market_rate(Variable):
    value_type = float
    entity = Person
    label = "New York CCAP regular monthly market rate"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.NY
    documentation = (
        "Prices scheduled and excess care periods before the special-needs "
        "substitution or payment differentials. New York City pays enhanced "
        "legally exempt group rates when the program meets its health or "
        "training requirements. Other districts retain standard group rates "
        "where no district enhancement has been confirmed."
    )
    reference = (
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-415.9",
        "https://ocfs.ny.gov/main/policies/external/2024/lcm/24-OCFS-LCM-22.pdf#page=9",
        "https://www.nyc.gov/assets/acs/pdf/earlycare/2024/FS023.pdf#page=2",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.ocfs.ccap.rates
        county_group = person.household("ny_ccap_county_group", period.this_year)
        provider_type = person("childcare_provider_type_group", period.this_year)
        age_group = person("ny_ccap_age_group", period.this_year)
        providers = provider_type.possible_values
        health = person("ny_ccap_enhanced_health", period.this_year)
        training = person("ny_ccap_enhanced_training", period.this_year)
        enhanced_fraction = select(
            [health & training, health | training],
            [
                p.enhanced_group.both[county_group],
                p.enhanced_group.single[county_group],
            ],
            default=0,
        )
        enhanced = (provider_type == providers.LE_GC) & (enhanced_fraction > 0)
        # OCFS rounds each enhanced period rate to the nearest whole dollar,
        # with a half dollar rounded up. Under-three group rates stay zero.
        has_group_rate = p.weekly[county_group]["LE_GC"][age_group] > 0
        period_rates = []
        for table in (p.weekly, p.daily, p.part_day):
            standard = table[county_group][provider_type][age_group]
            center = table[county_group]["DCC_SACC"][age_group]
            enhanced_rate = np.floor(center * enhanced_fraction + 0.5)
            period_rates.append(
                where(enhanced & has_group_rate, enhanced_rate, standard)
            )
        return ny_ccap_monthly_rate(person, period, parameters, *period_rates)
