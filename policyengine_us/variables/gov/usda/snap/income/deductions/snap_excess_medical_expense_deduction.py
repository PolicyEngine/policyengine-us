from policyengine_us.model_api import *


class snap_excess_medical_expense_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP excess medical expense deduction"
    unit = USD
    documentation = "Deduction from SNAP gross income for excess medical expenses"
    definition_period = MONTH
    reference = [
        "https://www.law.cornell.edu/uscode/text/7/2014#e_5",
        "https://www.law.cornell.edu/cfr/text/7/273.9#d_3",
    ]

    def formula(spm_unit, period, parameters):
        # 7 CFR 273.9(d)(3) allows the deduction only for elderly or
        # disabled household members (as defined in 271.2); nonhousehold
        # members and prorated ineligible members are not household
        # members, so their expenses do not count.
        person = spm_unit.members
        elderly = person("is_usda_elderly", period.this_year)
        disabled = person("is_usda_disabled", period.this_year)
        student = person("is_snap_ineligible_student", period.this_year)
        prorated = person("is_snap_prorated_income_member", period)
        moop = person("snap_allowable_medical_expenses", period) * ~(student | prorated)
        elderly_disabled_moop = spm_unit.sum(moop * (elderly | disabled))
        p = parameters(period).gov.usda.snap.income.deductions.excess_medical_expense
        excess = max_(elderly_disabled_moop - p.disregard, 0)
        # Calculate standard medical deduction (SMD).
        state = spm_unit.household("state_code_str", period)
        standard = p.standard[state]
        standard_claimable = where(excess > 0, standard, 0)
        # Return the greater of SMD and normal deduction.
        return max_(excess, standard_claimable)
