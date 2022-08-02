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
            "non_qualified_dividends", period
        )
        if qualified_dividends is None and non_qualified_dividends is None:
            raise ValueError(
                f"You did not provide an input for qualified dividends (`qualified_dividend_income`), non-qualified dividends (`non_qualified_dividends`), or total dividends (`dividend_income`). Please provide at least one of these inputs: if you provide total dividends, the model will impute qualified and ordinary dividends from that by splitting according to the percentage of dividends which is qualified from IRS statistics; if you provide qualified dividends, ordinary dividends, or both (if you provide one, we assume the other to be zero), the model calculates total dividends as the sum of those variables."
            )
        if qualified_dividends is None:
            qualified_dividends = dividend_income.default_array(person.count)
        if non_qualified_dividends is None:
            non_qualified_dividends = dividend_income.default_array(
                person.count
            )
        return qualified_dividends + non_qualified_dividends
