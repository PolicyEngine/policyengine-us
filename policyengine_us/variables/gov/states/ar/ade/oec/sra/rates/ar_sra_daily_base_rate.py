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
        "https://dese.ade.arkansas.gov/Files/SRA_Sliding_Fee_Scale_with_Rates_&_Copays--Statewide_Part_Time_20251101_OEC.pdf",
        "https://dese.ade.arkansas.gov/Files/SRA_Sliding_Fee_Scale_with_Rates_&_Copays--Benton-Washington_Co_Full_Time_20251101_OEC.pdf",
        "https://dese.ade.arkansas.gov/Files/SRA_Sliding_Fee_Scale_with_Rates_&_Copays--Benton-Washington_Co_Part_Time_20251101_OEC.pdf",
        "https://dese.ade.arkansas.gov/Files/October_2025_Provider_Call_10.7.25_OEC.pdf#page=4",
    )

    def formula(person, period, parameters):
        # Benton/Washington rates exceed Statewide for INFANT and TODDLER only;
        # PRESCHOOL and SCHOOL_AGED rates are identical across both zones. The
        # zone × age × care_type × time table preserves all four rate sheets
        # so the structure stays explicit even where two cells collapse.
        p = parameters(period).gov.states.ar.ade.oec.sra.rates
        zone = person.household("ar_sra_zone", period)
        age_category = person("ar_sra_age_category", period)
        care_type = person("ar_sra_care_type", period)
        time_category = person("ar_sra_time_category", period)
        return p.base_rate[zone][age_category][care_type][time_category]
