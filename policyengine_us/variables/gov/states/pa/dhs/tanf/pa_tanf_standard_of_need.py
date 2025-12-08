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

        county_group = household("pa_tanf_county_group", period)
        size = spm_unit("spm_unit_size", period)

        max_size = p.max_family_size_in_table
        capped_size = min_(size, max_size).astype(int)

        standard = p.standard_of_need.amount[county_group][capped_size]

        additional_people = max_(size - max_size, 0)
        additional_amount = (
            additional_people * p.standard_of_need.additional_person
        )

        return standard + additional_amount
