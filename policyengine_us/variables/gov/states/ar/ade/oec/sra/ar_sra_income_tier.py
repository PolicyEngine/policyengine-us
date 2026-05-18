from policyengine_us.model_api import *


class ArSraIncomeTier(Enum):
    LE_40 = "At or below 40% SMI"
    GT_40_LE_60 = "Above 40% and at or below 60% SMI"
    GT_60 = "Above 60% SMI"


class ar_sra_income_tier(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = ArSraIncomeTier
    default_value = ArSraIncomeTier.GT_60
    definition_period = MONTH
    defined_for = StateCode.AR
    label = "Arkansas SRA family income tier (% SMI)"
    reference = "https://dese.ade.arkansas.gov/Files/SRA_Sliding_Fee_Scale_with_Rates_&_Copays--Statewide_Full_Time_20251101_OEC.pdf"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ar.ade.oec.sra
        monthly_income = spm_unit("ar_sra_countable_income", period)
        monthly_smi = spm_unit("hhs_smi", period)
        ratio = where(monthly_smi > 0, monthly_income / monthly_smi, np.inf)
        return select(
            [
                ratio <= p.rates.no_copay_smi_threshold,
                ratio <= p.rates.partial_subsidy_smi_threshold,
            ],
            [ArSraIncomeTier.LE_40, ArSraIncomeTier.GT_40_LE_60],
            default=ArSraIncomeTier.GT_60,
        )
