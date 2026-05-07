from policyengine_us.model_api import *


class de_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Delaware TANF"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/delaware/16-Del-Admin-Code-SS-4000-4008"
    defined_for = "de_tanf_eligible"

    def formula(spm_unit, period, parameters):
        # Per DSSM 4008 / State Plan Exhibit 1 Step 3 (Benefit Calculation):
        # Net income = countable earned ($90 + $30 + 1/3 + childcare) + unearned
        p = parameters(period).gov.states.de.dhss.tanf

        countable_income = spm_unit("de_tanf_countable_income", period)

        # Deficit = Standard of Need - Net Income
        standard_of_need = spm_unit("de_tanf_standard_of_need", period)
        deficit = max_(standard_of_need - countable_income, 0)

        # Remainder = Deficit * 50%
        remainder = deficit * p.benefit.deficit_rate

        # Grant = min(Remainder, Payment Standard)
        payment_standard = spm_unit("de_tanf_payment_standard", period)

        return min_(remainder, payment_standard)
