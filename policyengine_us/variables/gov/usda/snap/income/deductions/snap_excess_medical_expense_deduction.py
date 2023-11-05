from policyengine_us.model_api import *


class snap_excess_medical_expense_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP excess medical expense deduction"
    unit = USD
    documentation = (
        "Deduction from SNAP gross income for excess medical expenses"
    )
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/uscode/text/7/2014#e_5"

    def formula(spm_unit, period, parameters):
        # Deduction applies to medical expenses incurred by elderly or disabled
        # members only.
        person = spm_unit.members
        elderly = person("is_usda_elderly", period)
        disabled = person("is_usda_disabled", period)
        moop = person("medical_out_of_pocket_expenses", period)
        elderly_disabled_moop = spm_unit.sum(moop * (elderly | disabled))
        p = parameters(
            period
        ).gov.usda.snap.income.deductions.excess_medical_expense
        disregard = p.disregard
        excess = max_(elderly_disabled_moop - disregard, 0)
        # Calculate standard medical deduction (SMD).
        state = spm_unit.household("state_code_str", period)
        standard = p.standard[state]
        standard_claimable = where(excess > 0, standard, 0)
        # Return the greater of SMD and normal deduction.
        return max_(excess, standard_claimable)
