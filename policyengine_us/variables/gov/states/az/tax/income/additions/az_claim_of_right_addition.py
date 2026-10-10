from policyengine_us.model_api import *


class az_claim_of_right_addition(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona addition for the federal claim of right repayment deduction"
    unit = USD
    documentation = (
        "The deduction under 26 U.S.C. 1341(a)(4) taken on the federal "
        "return for repaying income held under a claim of right, which "
        "Arizona adds to Arizona gross income (A.R.S. 43-1021(9); Form 140, "
        "line 18, item E). It is zero when federal tax is computed under "
        "section 1341(a)(5) or the federal return takes the standard "
        "deduction, because no deduction for the repayment is then taken."
    )
    definition_period = YEAR
    reference = (
        "https://www.azleg.gov/ars/43/01021.htm",
        # 2025 Form 140 instructions, line 18, item E
        "https://azdor.gov/sites/default/files/document/FORMS_INDIVIDUAL_2025_140i.pdf#page=9",
        # 2025 Arizona Claim of Right - Individual instructions, line 4
        "https://azdor.gov/sites/default/files/document/FORMS_INDIVIDUAL_2025_CLAIMOFRIGHT-INDIVIDUALi.pdf#page=2",
    )
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        deduction = tax_unit("claim_of_right_deduction", period)
        itemizes = tax_unit("tax_unit_itemizes", period)
        return deduction * itemizes
