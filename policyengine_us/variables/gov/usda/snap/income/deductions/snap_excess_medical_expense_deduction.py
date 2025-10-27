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
        # Sum prorated medical expenses for elderly/disabled members
        elderly_disabled_moop = add(
            spm_unit, period, ["snap_medical_out_of_pocket_expenses"]
        )
        p = parameters(
            period
        ).gov.usda.snap.income.deductions.excess_medical_expense
        excess = max_(elderly_disabled_moop - p.disregard, 0)
        # Calculate standard medical deduction (SMD).
        state = spm_unit.household("state_code_str", period)
        standard_claimable = where(excess > 0, p.standard[state], 0)
        # Return the greater of SMD and normal deduction.
        return max_(excess, standard_claimable)
