from policyengine_us.model_api import *


class pa_tanf_maximum_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Pennsylvania TANF maximum benefit"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/055/chapter183/chap183toc.html"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.pa.dhs.tanf
        household = spm_unit.household

        # Get county group
        county_group = household("pa_tanf_county_group", period)

        # Get household size
        size = spm_unit("spm_unit_size", period)

        # For households larger than 6, add incremental amount per person
        base_size = 6
        capped_size = min_(size, base_size).astype(int)

        # Get benefit schedule for each group
        group_1_schedule = p.benefit_amount.GROUP_1
        group_2_schedule = p.benefit_amount.GROUP_2
        group_3_schedule = p.benefit_amount.GROUP_3
        group_4_schedule = p.benefit_amount.GROUP_4

        # Select benefit based on county group and size
        from policyengine_us.variables.gov.states.pa.dhs.tanf.pa_tanf_county_group import (
            PATANFCountyGroup,
        )

        benefit = select(
            [
                county_group == PATANFCountyGroup.GROUP_1,
                county_group == PATANFCountyGroup.GROUP_2,
                county_group == PATANFCountyGroup.GROUP_3,
                county_group == PATANFCountyGroup.GROUP_4,
            ],
            [
                group_1_schedule[capped_size],
                group_2_schedule[capped_size],
                group_3_schedule[capped_size],
                group_4_schedule[capped_size],
            ],
        )

        # Add increment for each person beyond 6
        additional_people = max_(size - base_size, 0)
        additional_increment = p.additional_person_increment
        additional_benefit = additional_people * additional_increment

        # Return monthly benefit
        return benefit + additional_benefit
