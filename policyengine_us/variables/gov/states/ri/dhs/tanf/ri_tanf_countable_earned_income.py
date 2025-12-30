from policyengine_us.model_api import *


class ri_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Rhode Island TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/rhode-island/218-RICR-20-00-2.15",
        "https://rules.sos.ri.gov/Regulations/part/218-20-00-2",
    )
    defined_for = StateCode.RI

    def formula(spm_unit, period, parameters):
        # Per 218-RICR-20-00-2.15: Disregard $525 + 50% of remainder
        p = parameters(
            period
        ).gov.states.ri.dhs.tanf.income.earned_income_disregard
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        after_flat_disregard = max_(gross_earned - p.amount, 0)
        return after_flat_disregard * (1 - p.rate)
