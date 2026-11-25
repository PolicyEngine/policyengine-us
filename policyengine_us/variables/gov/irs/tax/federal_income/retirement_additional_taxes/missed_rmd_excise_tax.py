from policyengine_us.model_api import *


class missed_rmd_excise_tax(Variable):
    value_type = float
    entity = Person
    label = "Excise tax on missed required minimum distributions"
    documentation = "Form 5329 Part IX: 25% (10% if corrected timely) of required distributions not taken, less any waiver. IRA and employer plan shortfalls are measured separately."
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/4974",
        "https://www.irs.gov/instructions/i5329",
    )

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.irs.retirement_distributions.required_minimum_distributions
        # The deferred prior-year amount is due from the IRA or plan it came
        # from; it is measured with the IRA group here.
        ira_due = person("required_minimum_distribution_ira", period) + max_(
            0, person("rmd_prior_year_deferred_amount", period)
        )
        ira_shortfall = max_(0, ira_due - person("rmd_ira_distributions_taken", period))
        plan_shortfall = max_(
            0,
            person("required_minimum_distribution_employer_plan", period)
            - person("rmd_employer_plan_distributions_taken", period),
        )
        inherited_shortfall = max_(
            0,
            person("rmd_inherited_required_amount", period)
            - person("rmd_inherited_distributions_taken", period),
        )
        shortfall = max_(
            0,
            ira_shortfall
            + plan_shortfall
            + inherited_shortfall
            - max_(0, person("rmd_excise_waiver_amount", period)),
        )
        rate = where(
            person("rmd_shortfall_corrected_timely", period),
            p.corrected_excise_rate,
            p.excise_rate,
        )
        return rate * shortfall
