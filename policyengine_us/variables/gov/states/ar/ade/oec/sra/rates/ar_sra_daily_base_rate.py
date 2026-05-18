from policyengine_us.model_api import *


class ar_sra_daily_base_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Arkansas SRA daily base provider rate"
    definition_period = MONTH
    defined_for = "is_ar_sra_child_eligible"
    reference = (
        "https://dese.ade.arkansas.gov/Files/SRA_Sliding_Fee_Scale_with_Rates_&_Copays--Statewide_Full_Time_20251101_OEC.pdf",
        "https://dese.ade.arkansas.gov/Files/October_2025_Provider_Call_10.7.25_OEC.pdf#page=5",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ar.ade.oec.sra.rates
        zone = person.household("ar_sra_zone", period)
        age_category = person("ar_sra_age_category", period)
        care_type = person("ar_sra_care_type", period)
        time_category = person("ar_sra_time_category", period)
        rate = p.base_rate[zone][age_category][care_type][time_category]
        # Per OEC Oct 7 2025 Provider Call: Night/Weekend is a separate
        # 110%-of-FT category, not a FT/PT subdimension. Override with FT rate.
        time_categories = time_category.possible_values
        ft_rate = p.base_rate[zone][age_category][care_type][time_categories.FULL_TIME]
        is_night_weekend = care_type == care_type.possible_values.NIGHT_WEEKEND
        return where(is_night_weekend, ft_rate, rate)
