from policyengine_us.model_api import *


class va_claim_of_right_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia claim of right credit"
    unit = USD
    documentation = (
        "The method used for federal tax under 26 U.S.C. 1341 determines the "
        "method for Virginia. A filer whose federal tax is reduced under "
        "section 1341(a)(5) reduces Virginia tax by the Virginia tax "
        "attributable to including the repaid income in the earlier year. "
        "The amount is reported on the line for Virginia income tax "
        "withheld, so any excess over the year's tax is refunded. Under the "
        "federal deduction method there is no credit; the deduction flows "
        "through Virginia itemized deductions."
    )
    definition_period = YEAR
    reference = (
        "https://www.tax.virginia.gov/laws-rules-decisions/rulings-tax-commissioner/16-183",
        "https://www.tax.virginia.gov/laws-rules-decisions/rulings-tax-commissioner/20-35",
        # Va. Code 58.1-301(A), conformity of terms to federal income tax law
        "https://law.lis.virginia.gov/vacode/title58.1/chapter3/section58.1-301/",
    )
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        credit_applies = tax_unit("claim_of_right_credit_applies", period)
        person = tax_unit.members
        decrease = person("va_claim_of_right_prior_year_tax_decrease", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        prior_year_tax_decrease = tax_unit.sum(decrease * head_or_spouse)
        return where(credit_applies, prior_year_tax_decrease, 0)
