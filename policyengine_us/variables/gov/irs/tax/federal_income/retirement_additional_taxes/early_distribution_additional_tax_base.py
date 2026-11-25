from policyengine_us.model_api import *


class early_distribution_additional_tax_base(Variable):
    value_type = float
    entity = Person
    label = "Early distributions from plans, IRAs and annuities subject to the additional tax at the general rate"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/72#t",
        "https://www.law.cornell.edu/uscode/text/26/72#q",
    )

    def formula(person, period, parameters):
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
        return plans + annuities
