from policyengine_us.model_api import *


class id_tafi_work_incentive_amount(Variable):
    value_type = float
    entity = SPMUnit
    label = "Idaho TAFI work incentive table amount"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.251"
    )
    defined_for = StateCode.ID

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.id.tafi.work_incentive_table
        size = spm_unit("spm_unit_size", period.this_year)
        capped_size = min_(size, p.max_size)
        base_amount = p.amount[capped_size]
        additional_people = max_(size - p.max_size, 0)
        additional_amount = additional_people * p.additional_person
        return base_amount + additional_amount
