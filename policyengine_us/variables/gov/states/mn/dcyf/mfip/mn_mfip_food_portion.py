from policyengine_us.model_api import *


class mn_mfip_food_portion(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota MFIP food portion of Transitional Standard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/142G.17#stat.142G.17.5"
    )
    defined_for = StateCode.MN

    def formula(spm_unit, period, parameters):
        # Food portion of the Transitional Standard by family size.
        # Used with cash TS to compute the full TS for FWL and benefit
        # calculation per MN Stat. 142G.17, Subd. 5 & 7.
        p = parameters(period).gov.states.mn.dcyf.mfip.transitional_standard
        size = spm_unit("spm_unit_size", period.this_year)
        capped_size = min_(size, p.cash.max_unit_size)
        base_amount = p.food.amount[capped_size]
        additional_persons = max_(size - p.cash.max_unit_size, 0)
        return base_amount + additional_persons * p.food.additional_person
