from policyengine_us.model_api import *


class simplified_method_taxable_annuity(Variable):
    value_type = float
    entity = Person
    label = "Taxable qualified plan annuity under the Simplified Method"
    documentation = "Gross payments less (cost / expected monthly payments) per payment, the exclusion stopping when the cost is recovered (Pub. 575 Simplified Method Worksheet)."
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/72#d",
        "https://www.irs.gov/publications/p575",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.gross_income.annuities
        gross = max_(0, person("qualified_annuity_gross_payments", period))
        cost = max_(0, person("qualified_annuity_cost", period))
        combined = person("qualified_annuity_combined_starting_age", period)
        expected = where(
            combined > 0,
            p.simplified_method_payments_joint.calc(combined),
            p.simplified_method_payments.calc(
                person("qualified_annuity_starting_age", period)
            ),
        )
        months = person("qualified_annuity_monthly_payments_this_year", period)
        excluded = cost / expected * months
        remaining = max_(0, cost - person("qualified_annuity_cost_recovered", period))
        return max_(0, gross - min_(min_(excluded, remaining), gross))
