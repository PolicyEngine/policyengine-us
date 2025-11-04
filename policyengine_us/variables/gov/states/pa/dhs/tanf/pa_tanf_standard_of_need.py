from policyengine_us.model_api import *


class pa_tanf_standard_of_need(Variable):
    value_type = float
    entity = SPMUnit
    label = "Pennsylvania TANF standard of need"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "http://services.dpw.state.pa.us/oimpolicymanuals/cash/168_Determining_Eligibility_and_Payment_Amount/168_Appendix_A.htm"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.pa.dhs.tanf
        household = spm_unit.household

        # Get county group
        county_group = household("pa_tanf_county_group", period)

        # Get household size
        size = spm_unit("spm_unit_size", period)

        # For households larger than 6, add incremental amount per person
        capped_size = min_(size, 6).astype(int)

        # Get standard of need based on county group and size
        # Use county_group enum value as parameter key
        standard = p.standard_of_need.amount[county_group][capped_size]

        # Add increment for each person beyond 6
        additional_people = max_(size - 6, 0)
        additional_increment = p.standard_of_need.increment
        additional_amount = additional_people * additional_increment

        # Return monthly standard of need
        return standard + additional_amount
