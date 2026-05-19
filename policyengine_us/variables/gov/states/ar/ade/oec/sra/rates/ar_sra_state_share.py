from policyengine_us.model_api import *


class ar_sra_state_share(Variable):
    value_type = float
    entity = Person
    label = "Arkansas SRA state share of daily base rate"
    definition_period = MONTH
    defined_for = "is_ar_sra_child_eligible"
    reference = (
        "https://dese.ade.arkansas.gov/Files/SRA_Sliding_Fee_Scale_with_Rates_&_Copays--Statewide_Full_Time_20251101_OEC.pdf",
        "https://dese.ade.arkansas.gov/Files/SRA_Sliding_Fee_Scale_with_Rates_&_Copays--Statewide_Part_Time_20251101_OEC.pdf",
        "https://dese.ade.arkansas.gov/Files/SRA_Sliding_Fee_Scale_with_Rates_&_Copays--Benton-Washington_Co_Full_Time_20251101_OEC.pdf",
        "https://dese.ade.arkansas.gov/Files/SRA_Sliding_Fee_Scale_with_Rates_&_Copays--Benton-Washington_Co_Part_Time_20251101_OEC.pdf",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ar.ade.oec.sra.rates
        age_category = person("ar_sra_age_category", period)
        time_category = person("ar_sra_time_category", period)
        income_tier = person.spm_unit("ar_sra_income_tier", period)
        return p.state_share_by_tier[age_category][time_category][income_tier]
