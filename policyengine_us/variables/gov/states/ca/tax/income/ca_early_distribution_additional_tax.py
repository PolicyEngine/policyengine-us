from policyengine_us.model_api import *


class ca_early_distribution_additional_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "California additional tax on early distributions"
    documentation = (
        "FTB 3805P Part I: 2.5% (6% for SIMPLE IRA distributions in the "
        "first two years) of the early distributions subject to the federal "
        "additional tax, plus 2.5% of amounts California does not except."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/california/code-rtc/division-2/part-10/chapter-3/article-2/section-17085/",
        "https://www.ftb.ca.gov/forms/2025/2025-3805p-instructions.html",
    )
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.early_distribution_tax
        general = tax_unit_non_dep_add(
            tax_unit,
            period,
            [
                "early_distribution_additional_tax_base",
                "ca_early_distributions_not_excepted_in_california",
            ],
        )
        simple = tax_unit_non_dep_add(
            tax_unit, period, ["early_distribution_simple_ira_tax_base"]
        )
        return p.rate * general + p.simple_ira_rate * simple
