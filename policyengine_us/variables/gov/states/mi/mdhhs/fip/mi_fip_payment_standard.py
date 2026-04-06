from policyengine_us.model_api import *


class mi_fip_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Michigan FIP payment standard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/RF/Public/RFT/210.pdf",
        "https://www.michigan.gov/mdhhs/-/media/Project/Websites/mdhhs/Inside-MDHHS/Reports-and-Statistics---Human-Services/State-Plans-and-Federal-Regulations/TANF_State_Plan_2023.pdf",
    )
    defined_for = StateCode.MI

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mi.mdhhs.fip.payment_standard

        # Determine household size
        size = spm_unit("spm_unit_size", period)

        # For sizes 1-7, use the bracket schedule
        # For size 8+, use the size 7 amount plus additional per person
        max_household_size = p.max_household_size
        capped_size = min_(size, max_household_size)
        base_standard = p.base.calc(capped_size)

        # Add additional amount for household size 8+
        additional_persons = max_(size - max_household_size, 0)
        additional_amount = additional_persons * p.additional

        return base_standard + additional_amount
