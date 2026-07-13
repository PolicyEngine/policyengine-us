from policyengine_us.model_api import *


class snap_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "SNAP earned income"
    documentation = "Earned income for calculating the SNAP earned income deduction. Work-requirement-ineligible members' earned income counts in full (the 7 CFR 273.11(c)(1) treatment): their needs already leave the unit via snap_unit_size, and counting income in full guarantees a work-requirement disqualification can only reduce eligibility and benefits (7 U.S.C. 2015(o) is an eligibility limitation). The prior 273.11(c)(2) proration let households over the income limits at full composition qualify at the reduced size on the disqualified member's halved income, inverting the sign of ABAWD reforms at population scale."
    reference = "https://www.law.cornell.edu/cfr/text/7/273.9#b_1"
    unit = USD

    def formula(spm_unit, period):
        return spm_unit("snap_earned_income_person", period)
