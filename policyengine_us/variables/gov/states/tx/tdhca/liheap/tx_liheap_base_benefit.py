from policyengine_us.model_api import *


class tx_liheap_base_benefit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Texas LIHEAP base benefit"
    unit = USD
    documentation = "Base LIHEAP benefit amount before adjustments"
    reference = "https://www.tdhca.texas.gov/sites/default/files/2023-10/FY2024-LIHEAP-State-Plan.pdf"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tx.tdhca.liheap

        # Get household size
        size = spm_unit.nb_persons()

        # Map household size to adjustment factor
        # Using select to handle different household sizes
        size_names = [
            "one_person", "two_person", "three_person", "four_person",
            "five_person", "six_person", "seven_person", "eight_person",
            "nine_person", "ten_person"
        ]
        
        # Cap household size at 10 (maximum defined in adjustments)
        capped_size = min_(size, 10)
        
        # Get adjustment factor based on household size
        adjustment_factor = select(
            [capped_size == i for i in range(1, 11)],
            [
                p.household_size_adjustments.one_person,
                p.household_size_adjustments.two_person,
                p.household_size_adjustments.three_person,
                p.household_size_adjustments.four_person,
                p.household_size_adjustments.five_person,
                p.household_size_adjustments.six_person,
                p.household_size_adjustments.seven_person,
                p.household_size_adjustments.eight_person,
                p.household_size_adjustments.nine_person,
                p.household_size_adjustments.ten_person,
            ],
            default=p.household_size_adjustments.ten_person  # For 10+ person households
        )

        # Calculate base benefit using adjustment factor and maximum benefit
        base_amount = p.maximum_benefit * adjustment_factor

        return base_amount
