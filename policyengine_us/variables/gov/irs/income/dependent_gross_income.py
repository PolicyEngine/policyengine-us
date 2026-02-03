from policyengine_us.model_api import *

# Sources that depend on filing_status and would cause circular dependencies
CIRCULAR_SOURCES = {
    "taxable_unemployment_compensation": "unemployment_compensation",
    "taxable_social_security": "social_security",
}


class dependent_gross_income(Variable):
    value_type = float
    entity = Person
    label = "Gross income for dependents"
    unit = USD
    documentation = """
    Gross income for dependents, used for the qualifying relative income test
    under IRC 152(d)(1)(B). Mirrors irs_gross_income but calculates income for
    dependents (not head or spouse) instead of non-dependents.
    """
    definition_period = YEAR
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/61",
        "https://www.law.cornell.edu/uscode/text/26/152#d_1_B",
    ]

    def formula(person, period, parameters):
        sources = parameters(period).gov.irs.gross_income.sources
        total = 0
        is_dependent = ~person("is_tax_unit_head_or_spouse", period)
        for source in sources:
            # Replace sources that would cause circular dependencies
            if source in CIRCULAR_SOURCES:
                source = CIRCULAR_SOURCES[source]
            # Add positive values only - losses are deducted later.
            total += is_dependent * max_(0, add(person, period, [source]))
        return total
