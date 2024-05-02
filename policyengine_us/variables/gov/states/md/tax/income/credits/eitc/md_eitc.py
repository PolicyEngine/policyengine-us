from policyengine_us.model_api import *


class md_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD total EITC"
    unit = USD
    documentation = "Refundable and non-refundable Maryland EITC"
    definition_period = YEAR
    reference = "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-704-effective-until-6302023-for-earned-income"
    defined_for = StateCode.MD

    adds = ["md_non_refundable_eitc", "md_refundable_eitc"]

    # p = parameters(period).gov.states.md.tax.income.credits.eitc.montgomery
    # county = tax_unit.household("county", period) 
    # montgomery = county == "MONTGOMERY_COUNTY_MD"
    # md_eitc = md_non_refundable_eitc + md_refundable_eitc
    # return md_eitc + md_eitc * p.match * montgomery

    # queation: refundable or non_refundable or SUM
