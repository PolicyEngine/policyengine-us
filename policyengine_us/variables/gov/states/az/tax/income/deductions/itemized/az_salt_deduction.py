from policyengine_us.model_api import *


class az_salt_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona state and local tax deduction"
    unit = USD
    documentation = "Arizona Form 140 Schedule A"
    definition_period = YEAR
    defined_for = StateCode.AZ
    reference = (
        "https://law.justia.com/codes/arizona/2022/title-43/section-43-1042/",
        "https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2022_140SCHA_f.pdf#page=2",
    )
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions
        # The state and local income tax is reduced by the amount which is used 
        # to claim the Arizona charitable contributions credit
        # Since the Arizona charitable contributions credit is based on contributions 
        # to qulalifying foster care organizations, we do not reduce the salt deduction
        salt = tax_unit("state_and_local_sales_or_income_tax", period)
        filing_status = tax_unit("filing_status", period)
        cap = p.itemized.salt_and_real_estate.cap[filing_status]
        return min_(salt, cap)
