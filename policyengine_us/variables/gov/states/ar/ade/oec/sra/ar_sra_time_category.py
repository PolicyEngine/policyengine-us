from policyengine_us.model_api import *
from policyengine_us.tools.childcare import childcare_hours_for_daily_schedule


class ArSraTimeCategory(Enum):
    FULL_TIME = "Full-Time"
    PART_TIME = "Part-Time"


class ar_sra_time_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = ArSraTimeCategory
    default_value = ArSraTimeCategory.FULL_TIME
    definition_period = MONTH
    defined_for = StateCode.AR
    label = "Arkansas SRA time category"
    reference = (
        "https://dese.ade.arkansas.gov/Files/SRA_Sliding_Fee_Scale_with_Rates_&_Copays--Statewide_Full_Time_20251101_OEC.pdf",
        "https://dese.ade.arkansas.gov/Files/SRA_Sliding_Fee_Scale_with_Rates_&_Copays--Statewide_Part_Time_20251101_OEC.pdf",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ar.ade.oec.sra.rates
        # Unresolved hours retain full-time pricing; attendance and expense
        # rules still determine payment.
        hours = childcare_hours_for_daily_schedule(person, period)
        return where(
            (hours == 0) | (hours >= p.full_time_hours_threshold),
            ArSraTimeCategory.FULL_TIME,
            ArSraTimeCategory.PART_TIME,
        )
