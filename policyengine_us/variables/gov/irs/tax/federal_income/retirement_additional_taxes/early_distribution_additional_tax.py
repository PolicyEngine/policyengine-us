from policyengine_us.model_api import *


class early_distribution_additional_tax(Variable):
    value_type = float
    entity = Person
    label = "Additional tax on early distributions"
    documentation = "Form 5329 Part I line 4: 10% (25% for SIMPLE IRA distributions in the first two years) of early distributions not excepted."
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/72#t",
        "https://www.law.cornell.edu/uscode/text/26/72#q",
        "https://www.irs.gov/instructions/i5329",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.retirement_distributions.early_distribution_tax
        plans = max_(
            0,
            person("early_distributions_from_retirement_plans", period)
            - person("early_distribution_allowed_exceptions", period),
        )
        annuities = max_(
            0,
            person("early_distributions_from_annuity_contracts", period)
            - max_(person("early_distribution_exceptions_annuity", period), 0),
        )
        simple = person("early_distribution_simple_ira_tax_base", period)
        return p.rate * plans + p.annuity_rate * annuities + p.simple_ira_rate * simple
