from policyengine_us.model_api import *


class ak_atap(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alaska ATAP benefit"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.525",
        "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.523",
    )
    defined_for = "ak_atap_eligible"

    def formula(spm_unit, period, parameters):
        # NOTE: The following Alaska ATAP features are not modeled:
        #
        # Unit types not modeled:
        #   1. Child-only units - Only adult-included units are implemented
        #   2. Two-parent incapacitated - Both parents treated as able to work
        #
        # Benefit adjustments not modeled:
        #   3. Shelter cost reduction - Benefits reduced for families with low
        #      shelter costs based on regional utility standards
        #   4. Summer reduction - Two-parent families receive reduced benefits
        #      during summer months (July-September)
        #
        # See 7 AAC 45.520-525 for full eligibility and benefit rules.

        p = parameters(period).gov.states.ak.dpa.atap
        need_standard = spm_unit("ak_atap_need_standard", period)
        countable_income = spm_unit("ak_atap_countable_income", period)

        # Per 7 AAC 45.525: Payment = (Need Standard - Countable Income)
        # multiplied by (size 2 max payment / size 2 need standard)
        # The ratio uses fixed size-2 values, not the family's actual size
        income_deficit = max_(need_standard - countable_income, 0)
        size_2_max = p.payment.base
        # Per 7 AAC 45.525: ratable reduction formula always uses size-2 as base
        size_2_need = p.need_standard.amount["2"]
        ratable_reduction = size_2_max / size_2_need
        return income_deficit * ratable_reduction
