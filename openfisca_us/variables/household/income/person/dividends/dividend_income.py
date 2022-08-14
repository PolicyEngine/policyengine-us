from openfisca_us.model_api import *
from openfisca_us import CountryTaxBenefitSystem


class dividend_income(Variable):
    value_type = float
    entity = Person
    label = "Dividend income"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        simulation = person.simulation
        qualified_dividends = simulation.get_array(
            "qualified_dividend_income", period
        )
        non_qualified_dividends = simulation.get_array(
            "non_qualified_dividend_income", period
        )
        zeros = np.zeros(person.count)
        if qualified_dividends is None and non_qualified_dividends is None:
            return zeros
        if qualified_dividends is None:
            qualified_dividends = zeros
        if non_qualified_dividends is None:
            non_qualified_dividends = zeros
        return qualified_dividends + non_qualified_dividends
