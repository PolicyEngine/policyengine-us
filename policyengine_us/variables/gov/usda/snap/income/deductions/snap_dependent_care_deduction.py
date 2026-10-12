from policyengine_us.model_api import *


class snap_dependent_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP dependent care deduction"
    unit = USD
    documentation = (
        "Deduction from SNAP gross income for dependent care. "
        "Non-modeled provision: 7 CFR 273.9(d)(4) allows these costs "
        "only when necessary for a household member to search for, "
        "accept, or continue employment, comply with SNAP E&T, or "
        "attend training or education preparatory to employment; we "
        "do not track that condition at the moment, so all reported "
        "childcare and adult dependent care expenses flow into the "
        "deduction."
    )
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2014#e_3",
        "https://www.law.cornell.edu/cfr/text/7/273.9#d_4",
        "https://www.law.cornell.edu/cfr/text/7/273.11#c_2_iii",
    )

    def formula(spm_unit, period, parameters):
        # Per 7 CFR 273.9(d)(4), deductible costs cover care of a child
        # under age 18 or an incapacitated person of any age.
        expenses = add(spm_unit, period, ["childcare_expenses", "care_expenses"])
        share = spm_unit("snap_expense_counted_share", period)
        return expenses * share
