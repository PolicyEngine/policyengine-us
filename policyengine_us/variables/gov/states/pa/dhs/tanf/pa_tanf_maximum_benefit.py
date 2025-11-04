from policyengine_us.model_api import *


class pa_tanf_maximum_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Pennsylvania TANF maximum benefit"
    documentation = "Pennsylvania TANF Family Size Allowance (FSA) is the maximum monthly benefit amount based on household size, before income deductions."
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PA
    reference = "55 Pa. Code Chapter 183, Appendix B, Table 3"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.pa.dhs.tanf

        # Get household size
        size = spm_unit("spm_unit_size", period)

        # Get benefit amounts for sizes 1-8
        benefit_schedule = p.benefit_amount

        # For households larger than 8, add incremental amount per person
        base_size = 8
        # Use .astype(int) to ensure proper indexing
        capped_size = min_(size, base_size).astype(int)

        # Get scheduled benefit for household size (keys are strings in parameter file)
        scheduled_benefit = select(
            [
                capped_size == 1,
                capped_size == 2,
                capped_size == 3,
                capped_size == 4,
                capped_size == 5,
                capped_size == 6,
                capped_size == 7,
                capped_size == 8,
            ],
            [
                benefit_schedule["1"],
                benefit_schedule["2"],
                benefit_schedule["3"],
                benefit_schedule["4"],
                benefit_schedule["5"],
                benefit_schedule["6"],
                benefit_schedule["7"],
                benefit_schedule["8"],
            ],
        )

        # Add increment for each person beyond 8
        additional_people = max_(size - base_size, 0)
        additional_increment = p.additional_person_increment
        additional_benefit = additional_people * additional_increment

        # Monthly benefit
        monthly_benefit = scheduled_benefit + additional_benefit

        # Return annual benefit (used in yearly calculation)
        return monthly_benefit * 12
