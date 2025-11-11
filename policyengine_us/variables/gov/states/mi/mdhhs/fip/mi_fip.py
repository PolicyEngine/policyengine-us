from policyengine_us.model_api import *


class mi_fip(Variable):
    value_type = float
    entity = SPMUnit
    label = "Michigan Family Independence Program"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.michigan.gov/mdhhs/-/media/Project/Websites/mdhhs/Inside-MDHHS/Reports-and-Statistics---Human-Services/State-Plans-and-Federal-Regulations/TANF_State_Plan_2023.pdf",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/520.pdf",
    )
    defined_for = "mi_fip_eligible"

    def formula(spm_unit, period, parameters):
        # Benefit calculation: Payment Standard - Countable Income
        # Per BEM 520
        payment_standard = spm_unit("mi_fip_payment_standard", period)
        countable_income = spm_unit("mi_fip_countable_income", period)

        return max_(payment_standard - countable_income, 0)
