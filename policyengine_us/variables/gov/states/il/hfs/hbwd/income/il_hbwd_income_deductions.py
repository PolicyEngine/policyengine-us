from policyengine_us.model_api import *


class il_hbwd_income_deductions(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Illinois Health Benefits for Workers with Disabilities income deductions"
    definition_period = MONTH
    reference = (
        "https://ilga.gov/commission/jcar/admincode/089/089001200I03700R.html",
        "https://ilga.gov/commission/jcar/admincode/089/089001200I05100R.html",
        "https://hfs.illinois.gov/medicalprograms/hbwd/eligibility.html",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # HBWD uses the same work expense deductions as AABD per
        # 89 Ill. Admin. Code § 120.510 referencing § 120.370 MANG(AABD)
        # Currently implemented deductions include:
        # - State withheld income tax
        # - Employee Social Security tax
        # - Child care expenses ($128-$160/child based on hours)
        # Note: Transportation, meals, uniforms, union dues, insurance
        # premiums, retirement withholdings, and disability work items
        # are not yet implemented
        return person("il_aabd_expense_exemption_person", period)
