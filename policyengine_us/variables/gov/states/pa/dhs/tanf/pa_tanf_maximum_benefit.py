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
        capped_size = min_(size, 6).astype(int)

        # Get benefit based on county group and size
        # Use county_group enum value as parameter key
        benefit = p.payment_standard.amount[county_group][capped_size]

        # Add increment for each person beyond 6
        additional_people = max_(size - 6, 0)
        additional_increment = p.payment_standard.increment
        additional_benefit = additional_people * additional_increment

        # Return monthly benefit
        return benefit + additional_benefit
