from policyengine_us.model_api import *


class ok_liheap_net_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Oklahoma LIHEAP net income for regular heating assistance"
    defined_for = StateCode.OK
    reference = (
        # OAC 340:20-1-11(a)(4), (c): do not repeat deductions already
        # applied to ineligible members before the gross-income test.
        "https://prod-ok-administrativerules.tecuity.com/api/BlobStorageGetFile?storageContainer=TitleHtml&name=Title_340.html",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        gross_income = spm_unit("ok_liheap_gross_income", period)
        eligible = person("ok_liheap_immigration_eligible", period)
        personal_deductions = spm_unit.sum(
            person("ok_liheap_income_deductions", period) * eligible
        )
        receives_subsidy = spm_unit("ok_child_care_subsidies", period) > 0
        copay = spm_unit("ok_ccs_copay", period, options=[ADD])
        # The SPM copay has no payer attribution. Deduct it once at net,
        # without assigning it to an ineligible tax unit before the gross
        # test. Gross income can be overstated when that person paid it.
        childcare_deduction = where(receives_subsidy, copay, 0)
        return max_(gross_income - personal_deductions - childcare_deduction, 0)
