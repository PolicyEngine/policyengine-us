from policyengine_us.model_api import *


class il_hbwd_income_deductions(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Illinois Health Benefits for Workers with Disabilities income deductions"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-120.370",
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-120.510",
        "https://hfs.illinois.gov/medicalprograms/hbwd/eligibility.html",
    )
    defined_for = StateCode.IL

    adds = ["il_aabd_expense_exemption_person"]
    # HBWD uses the same work expense deductions as AABD per
    # 89 Ill. Admin. Code § 120.510 referencing § 120.370 MANG(AABD)
    # Currently implemented deductions include:
    # - State withheld income tax
    # - Employee Social Security tax
    # - Child care expenses ($128-$160/child based on hours)
    # Note: Transportation, meals, uniforms, union dues, insurance
    # premiums, retirement withholdings, and disability work items
    # are not yet implemented
