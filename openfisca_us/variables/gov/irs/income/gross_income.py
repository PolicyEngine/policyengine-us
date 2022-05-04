from openfisca_us.model_api import *


class irs_gross_income(Variable):
    value_type = float
    entity = Person
    label = "Gross income"
    unit = USD
    documentation = "Gross income, as defined in the Internal Revenue Code."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/61"

    def formula(person, period, parameters):
        sources = parameters(period).irs.gross_income.sources
        total = 0
        for source in sources:
            # Add positive values only - losses are deducted later.
            total += max_(0, add(person, period, [source]))
        return total
