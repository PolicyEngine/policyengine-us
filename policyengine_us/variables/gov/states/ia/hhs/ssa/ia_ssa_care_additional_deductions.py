from policyengine_us.model_api import *


class ia_ssa_care_additional_deductions(Variable):
    value_type = float
    entity = Person
    label = "Iowa SSA approved additional care income deductions"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.IA
    documentation = "Verified monthly deductions from care income beyond those the model applies: unmet medical needs; for in-home health-related care, the allowance for a dependent other than an SSI-ineligible child in the tax unit; for residential care, the spouse and dependent diversions (omit the spouse diversion in a month of entry, when the SSI couple rate is deducted instead), income used that month to pay for care in another facility or setting and, for a resident who receives no SSI, one-half of impairment-related work expenses, because this input is subtracted after the one-half earnings exclusion. Enter no impairment-related work expenses for an SSI recipient: SSA's payment already offsets them. Enter a deduction a couple shares on one spouse only; in-home care adds the couple's entries together. Excludes the home maintenance, dependent-child and personal needs allowances, the entry-month SSI rate deduction and the $65 and one-half earnings exclusions. Key each amount to its month; a yearly entry is spread evenly over the months."
    reference = (
        # 441 IAC 52.1(3)"a"
        "https://www.legis.iowa.gov/docs/iac/chapter/441.52.pdf#page=1",
        # PDF pages 42-44, 59, 61-65, 68
        "https://hhs.iowa.gov/media/3987/download?inline=#page=42",
    )

    def formula(person, period, parameters):
        # A formula stops a one-month input from carrying into later months.
        return 0
