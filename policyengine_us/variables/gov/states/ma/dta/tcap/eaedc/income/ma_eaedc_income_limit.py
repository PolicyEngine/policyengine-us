from policyengine_us.model_api import *

class MassachusettsEAEDCLivingArrangement(Enum):
    A = "A"  # Living Arrangement A
    B = "B"  # Living Arrangement B
    C = "C"  # Living Arrangement C
    D = "D"  # Living Arrangement D
    E = "E"  # Living Arrangement E
    F = "F"  # Living Arrangement F
    H = "H"  # Living Arrangement H
    NONE = "None"


class ma_eaedc_income_limit(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = MassachusettsEAEDCLivingArrangement
    label = "Massachusetts EAEDC income limit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-440"
    )
    default_value = MassachusettsEAEDCLivingArrangement.NONE
    
    def formula(spm_unit, period, parameters):
        n = spm_unit("spm_unit_size", period)
       # MassachusettsEAEDCLivingArrangement = spm_unit("MassachusettsEAEDCLivingArrangement",period)
        p_income_limit = parameters(period).gov.states.ma.dta.tcap.eaedc.income
        p1 = p_income_limit.base[MassachusettsEAEDCLivingArrangement]
        pn = p_income_limit.increment[MassachusettsEAEDCLivingArrangement]
        return  p1+pn*(n-1)
        