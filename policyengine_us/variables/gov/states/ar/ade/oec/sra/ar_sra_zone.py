from policyengine_us.model_api import *


class ArSraZone(Enum):
    BENTON_WASHINGTON = "Benton/Washington"
    STATEWIDE = "Statewide"


class ar_sra_zone(Variable):
    value_type = Enum
    entity = Household
    possible_values = ArSraZone
    default_value = ArSraZone.STATEWIDE
    definition_period = MONTH
    defined_for = StateCode.AR
    label = "Arkansas SRA rate zone"
    reference = (
        "https://dese.ade.arkansas.gov/Files/SRA_Sliding_Fee_Scale_with_Rates_&_Copays--Benton-Washington_Co_Full_Time_20251101_OEC.pdf",
        "https://dese.ade.arkansas.gov/Files/SRA_Sliding_Fee_Scale_with_Rates_&_Copays--Statewide_Full_Time_20251101_OEC.pdf",
    )

    def formula(household, period, parameters):
        # Belt-and-suspenders: defined_for filters output but doesn't gate
        # the lookup, so guard county_str against non-AR rows.
        state = household("state_code_str", period.this_year)
        county = household("county_str", period.this_year)
        in_benton_washington = (state == "AR") & (
            (county == "BENTON_COUNTY_AR") | (county == "WASHINGTON_COUNTY_AR")
        )
        return where(
            in_benton_washington,
            ArSraZone.BENTON_WASHINGTON,
            ArSraZone.STATEWIDE,
        )
