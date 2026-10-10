from policyengine_us.model_api import *


class az_claim_of_right_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona claim of right credit"
    unit = USD
    documentation = (
        "When a filer repays more than the threshold of income included in "
        "an earlier year under a claim of right, Arizona tax is the tax "
        "computed without a deduction for the repayment, minus the decrease "
        "in the earlier year's Arizona tax from excluding the repaid income "
        "(A.R.S. 43-1029(B)). Arizona allows no deduction instead, whichever "
        "method the federal return uses. Any excess of the decrease over the "
        "year's tax is refunded (A.R.S. 43-1029(C)). Reported on Form 140, "
        "line 54, box 54b, from the Arizona Claim of Right form, line 8."
    )
    definition_period = YEAR
    reference = (
        "https://www.azleg.gov/ars/43/01029.htm",
        # 2025 Arizona Claim of Right - Individual instructions
        "https://azdor.gov/sites/default/files/document/FORMS_INDIVIDUAL_2025_CLAIMOFRIGHT-INDIVIDUALi.pdf#page=1",
        # 2025 Form 140 instructions, line 54
        "https://azdor.gov/sites/default/files/document/FORMS_INDIVIDUAL_2025_140i.pdf#page=25",
        # ITP 16-1
        "https://azdor.gov/sites/default/files/2023-03/PROCEDURES_INDIV_2016_ITP16-1.pdf#page=1",
    )
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income.credits.claim_of_right
        repayment = tax_unit("tax_unit_claim_of_right_repayment", period)
        person = tax_unit.members
        decrease = person("az_claim_of_right_prior_year_tax_decrease", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        prior_year_tax_decrease = tax_unit.sum(decrease * head_or_spouse)
        return where(repayment > p.threshold, prior_year_tax_decrease, 0)
