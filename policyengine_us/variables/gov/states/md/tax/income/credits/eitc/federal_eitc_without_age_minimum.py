from policyengine_us.model_api import *


class federal_eitc_without_age_minimum(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal EITC without age minimum"
    unit = USD
    documentation = "The federal EITC with the minimum age condition ignored; the maximum age condition still applies."
    definition_period = YEAR
    reference = "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-704-effective-until-6302023-for-earned-income"
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        # Per Md. Code Tax-Gen. § 10-704(c)(3), childless filers claim the
        # state EITC as if the federal § 32 minimum-age requirement did not
        # apply. Recompose the federal EITC without the minimum age; the
        # maximum age in § 32(c)(1)(A)(ii)(II) and other federal § 32 rules
        # (investment income, SSN) still apply.
        person = tax_unit.members
        has_child = tax_unit("eitc_child_count", period) > 0
        # Relative parameter reference break branching in some states that
        # modify EITC age limits.
        max_age = parameters.gov.irs.credits.eitc.eligibility.age.max(period)
        is_filer_or_spouse = ~person("is_tax_unit_dependent", period)
        below_max_age = person("age", period) <= max_age
        meets_max_age = has_child | tax_unit.any(below_max_age & is_filer_or_spouse)
        phased_in = tax_unit("eitc_phased_in", period)
        maximum = tax_unit("eitc_maximum", period)
        reduction = tax_unit("eitc_reduction", period)
        investment_eligible = tax_unit("eitc_investment_income_eligible", period)
        filer_has_ssn = tax_unit("filer_meets_eitc_identification_requirements", period)
        return (
            min_(phased_in, max_(0, maximum - reduction))
            * investment_eligible
            * filer_has_ssn
            * meets_max_age
        )
