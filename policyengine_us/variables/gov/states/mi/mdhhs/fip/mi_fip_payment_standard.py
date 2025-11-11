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
        p = parameters(period).gov.states.mi.mdhhs.fip

        # Determine household size
        size = spm_unit.nb_persons()

        # Get payment standard from bracket schedule
        schedule = p.payment_standard.amounts

        # For sizes 1-7, use the bracket schedule
        # For size 8+, use the size 7 amount plus additional per person
        max_bracket_size = 7  # Maximum size in bracket schedule
        size_capped = min_(size, max_bracket_size)
        base_standard = schedule.calc(size_capped)

        # Add additional amount for household size 8+
        additional_persons = max_(size - max_bracket_size, 0)
        additional_amount = (
            additional_persons * p.payment_standard.additional_person_increment
        )

        return base_standard + additional_amount
