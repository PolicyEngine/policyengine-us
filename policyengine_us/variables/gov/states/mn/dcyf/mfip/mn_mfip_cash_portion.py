from policyengine_us.model_api import *


class mn_mfip_cash_portion(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota MFIP Transitional Standard (cash portion)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/142G.17#stat.142G.17.5",
        "https://www.house.mn.gov/hrd/pubs/ss/ssmfip.pdf#page=5",
    )
    defined_for = StateCode.MN

    def formula(spm_unit, period, parameters):
        # Per MN Stat. 142G.17, Subd. 5:
        # Cash portion of the Transitional Standard by family size.
        # The food portion is in a separate variable (mn_mfip_food_portion).
        p = parameters(period).gov.states.mn.dcyf.mfip.transitional_standard.cash
        size = spm_unit("spm_unit_size", period.this_year)
        capped_size = min_(size, p.max_unit_size)
        base_amount = p.amount[capped_size]
        additional_persons = max_(size - p.max_unit_size, 0)
        return base_amount + additional_persons * p.additional_person
