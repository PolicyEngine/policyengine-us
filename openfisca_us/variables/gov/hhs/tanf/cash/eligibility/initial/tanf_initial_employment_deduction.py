from openfisca_us.model_api import *


class tanf_initial_employment_deduction(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "TANF IED (Initial Employment Deduction)"
    documentation = "The amount deducted from the countable earnings of a TANF application when calculating initial eligibility."
    unit = USD

    def formula(spm_unit, period, parameters):
        family_size = spm_unit("spm_unit_size", period)
        state = spm_unit.household("state_code_str", period)
        ied = parameters(
            period
        ).gov.hhs.tanf.cash.eligibility.initial.deductions.employment
        per_earner = ied.earner[state]
        per_household = ied.household[state][family_size]
        earners = spm_unit.members("market_income", period) > 0
        earner_count = spm_unit.sum(earners)
        return (per_household + (per_earner * earner_count)) * MONTHS_IN_YEAR
