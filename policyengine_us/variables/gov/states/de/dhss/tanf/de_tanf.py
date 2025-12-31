from policyengine_us.model_api import *


class de_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Delaware TANF"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/delaware/"
        "16-Del-Admin-Code-SS-4000-4008"
    )
    defined_for = "de_tanf_eligible"

    def formula(spm_unit, period, parameters):
        # Per DSSM 4008: Grant calculation
        # Step 1: Deficit = Standard of Need - Net Income
        # Step 2: Remainder = Deficit * 50%
        # Step 3: Grant = min(Remainder, Payment Standard)
        p = parameters(period).gov.states.de.dhss.tanf

        standard_of_need = spm_unit("de_tanf_standard_of_need", period)
        net_income = spm_unit("de_tanf_countable_net_income", period)

        # Step 1: Calculate deficit
        deficit = max_(standard_of_need - net_income, 0)

        # Step 2: Calculate remainder (50% of deficit)
        remainder = deficit * p.benefit.deficit_rate

        # Step 3: Grant is lesser of remainder or payment standard
        payment_standard = spm_unit("de_tanf_payment_standard", period)

        return min_(remainder, payment_standard)
