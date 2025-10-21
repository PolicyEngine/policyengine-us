from policyengine_us.model_api import *


class fl_tanf_earned_income_disregard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Florida TANF earned income disregard"
    unit = USD
    definition_period = MONTH
    reference = "Florida Statute § 414.095"
    documentation = "Two-step earned income disregard: (1) $90 per person standard disregard, then (2) $200 plus 50% of remainder"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.fl.dcf.tanf.income_disregards

        gross_earned = spm_unit("fl_tanf_gross_earned_income", period)
        family_size = spm_unit.nb_persons()

        # Step 1: Standard disregard of $90 per person
        standard_disregard = p.earned_per_person * family_size
        after_standard = max_(gross_earned - standard_disregard, 0)

        # Step 2: Work incentive disregard - first $200 plus 50% of remainder
        flat_disregard = p.earned_flat
        percentage_disregard = p.earned_percentage

        after_flat = max_(after_standard - flat_disregard, 0)
        percentage_amount = after_flat * percentage_disregard

        # Total disregard is all amounts disregarded
        total_disregard = (
            standard_disregard + flat_disregard + percentage_amount
        )

        return min_(total_disregard, gross_earned)
