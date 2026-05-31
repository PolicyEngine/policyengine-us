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
        "https://dese.ade.arkansas.gov/Files/SRA_Sliding_Fee_Scale_with_Rates_&_Copays--Statewide_Part_Time_20251101_OEC.pdf",
        "https://dese.ade.arkansas.gov/Files/SRA_Sliding_Fee_Scale_with_Rates_&_Copays--Benton-Washington_Co_Full_Time_20251101_OEC.pdf",
        "https://dese.ade.arkansas.gov/Files/SRA_Sliding_Fee_Scale_with_Rates_&_Copays--Benton-Washington_Co_Part_Time_20251101_OEC.pdf",
    )

    def formula(person, period, parameters):
        # Source conflict: CCDF State Plan §2.3.1(b) describes a no-cost-of-care
        # waiver for families at or below 75% SMI, while the Nov 2025 operational
        # rate sheet only zeroes the copay for families at or below 40% SMI. The
        # model follows the rate sheet (40%) because it is the operational
        # document the agency uses to compute family copays. The 75% State Plan
        # provision is not modeled.
        base = person("ar_sra_daily_base_rate", period)
        state_share = person("ar_sra_state_share", period)
        return base * (1 - state_share)
