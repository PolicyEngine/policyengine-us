from policyengine_us.model_api import *


class ar_sra_daily_copay(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Arkansas SRA daily family copay"
    definition_period = MONTH
    defined_for = "is_ar_sra_child_eligible"
    reference = (
        "https://dese.ade.arkansas.gov/Files/SRA_Sliding_Fee_Scale_with_Rates_&_Copays--Statewide_Full_Time_20251101_OEC.pdf",
    )

    def formula(person, period, parameters):
        base = person("ar_sra_daily_base_rate", period)
        state_share = person("ar_sra_state_share", period)
        return base * (1 - state_share)
