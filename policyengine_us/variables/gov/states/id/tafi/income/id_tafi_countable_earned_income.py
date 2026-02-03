from policyengine_us.model_api import *


class id_tafi_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Idaho TAFI countable earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.252"
    )
    defined_for = StateCode.ID

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.id.tafi.income.earned
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        # Per IDAPA 16.03.08.252: 60% of gross earned income is subtracted
        # from the work incentive table amount
        return gross_earned * p.countable_rate
