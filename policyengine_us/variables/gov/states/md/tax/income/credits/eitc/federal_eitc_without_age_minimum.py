from policyengine_us.model_api import *


class federal_eitc_without_age_minimum(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal EITC without age minimum"
    unit = USD
    documentation = "The federal EITC with the minimum age condition ignored."
    definition_period = YEAR
    reference = "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-704-effective-until-6302023-for-earned-income"
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        # Per Md. Code Tax-Gen. § 10-704(c)(3), unmarried childless filers
        # claim the state EITC as if the federal § 32 minimum-age requirement
        # did not apply. Recompose the federal EITC without the demographic
        # gate; other federal § 32 rules (investment income, SSN) still apply.
        phased_in = tax_unit("eitc_phased_in", period)
        maximum = tax_unit("eitc_maximum", period)
        reduction = tax_unit("eitc_reduction", period)
        investment_eligible = tax_unit("eitc_investment_income_eligible", period)
        filer_has_ssn = tax_unit("filer_meets_eitc_identification_requirements", period)
        return (
            min_(phased_in, max_(0, maximum - reduction))
            * investment_eligible
            * filer_has_ssn
        )
