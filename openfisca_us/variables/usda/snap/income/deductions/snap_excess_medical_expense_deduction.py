from openfisca_us.model_api import *


class snap_excess_medical_expense_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP excess medical expense deduction"
    unit = USD
    documentation = (
        "Deduction from SNAP gross income for excess medical expenses"
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/7/2014#e_5"

    def formula(spm_unit, period, parameters):
        # Deduction applies to medical expenses incurred by elderly or disabled
        # members only.
        person = spm_unit.members
        elderly = person("is_usda_elderly", period)
        disabled = person("is_usda_disabled", period)
        moop = person("medical_out_of_pocket_expenses", period)
        elderly_disabled_moop = spm_unit.sum(moop * (elderly | disabled))
        p = parameters(period).usda.snap.deductions.excess_medical_expense
        return max_(elderly_disabled_moop - p.threshold, 0)
