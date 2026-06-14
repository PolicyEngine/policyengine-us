from policyengine_us.model_api import *


class ky_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kentucky CCAP countable income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.KY
    reference = "https://apps.legislature.ky.gov/services/karmaservice/documents/10239/ToPDF?markup=false#page=7"

    def formula(spm_unit, period, parameters):
        # Section 8(2): gross income received or anticipated by the applicant
        # and responsible adult, from the counted sources (Section 8(2), (4)).
        p = parameters(period).gov.states.ky.dcbs.ccap.income.countable_income
        gross = add(spm_unit, period, p.sources)
        # Section 8(5)(a): deduct actual, legally obligated child support paid
        # to a party not living in the family's residence. Section 8(5)(b)'s
        # self-employment operating-cost deduction is inherent in
        # self_employment_income, which is already net of expenses.
        child_support = add(spm_unit, period, ["child_support_expense"])
        return max_(0, gross - child_support)
