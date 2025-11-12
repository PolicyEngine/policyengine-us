from policyengine_us.model_api import *


class tn_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Tennessee TANF"
    unit = USD
    definition_period = MONTH
    documentation = (
        "Tennessee Families First TANF benefit using fill-the-gap methodology. "
        "The benefit equals the minimum of: (1) the payment standard (SPA or DGPA), "
        "or (2) the deficit (Consolidated Need Standard minus countable income). "
        "No payment is made if the calculated benefit is less than the minimum grant."
    )
    reference = (
        "https://www.law.cornell.edu/regulations/tennessee/Tenn-Comp-R-Regs-1240-01-50-.20",
        "Tennessee Administrative Code § 1240-01-50-.20 - Standard of Need/Income",
        "https://www.tn.gov/humanservices/for-families/families-first-tanf.html",
    )
    defined_for = StateCode.TN

    def formula(spm_unit, period, parameters):
        # Check eligibility
        eligible = spm_unit("tn_tanf_eligible", period)

        # Get payment standard (SPA or DGPA based on eligibility)
        payment_standard = spm_unit("tn_tanf_payment_standard", period)

        # Calculate countable income
        countable_income = spm_unit("tn_tanf_countable_income", period)

        # Fill-the-gap budgeting methodology per Tenn. Comp. R. & Regs. 1240-01-50-.20:
        # "The monthly grant equals the smaller of a maximum payment amount by family size
        # (SPA or DGPA, as appropriate) or the deficit if it is ten dollars ($10) or more."
        #
        # Step 1: Get Consolidated Need Standard (CNS) based on family size
        p = parameters(period).gov.states.tn.dhs.tanf
        unit_size = spm_unit.nb_persons()
        max_size = p.eligibility.max_family_size
        capped_size = min_(unit_size, max_size)
        cns = p.benefit.consolidated_need_standard[capped_size]

        # Step 2: Calculate deficit = CNS - countable_income
        deficit = max_(cns - countable_income, 0)

        # Step 3: Benefit = min(payment_standard, deficit)
        calculated_benefit = min_(payment_standard, deficit)

        # Apply minimum grant threshold
        minimum_grant = p.benefit.minimum_grant

        # If benefit is less than minimum, no payment is made
        benefit = where(
            calculated_benefit >= minimum_grant, calculated_benefit, 0
        )

        # Only pay if eligible
        return where(eligible, benefit, 0)
