from policyengine_us.model_api import *


class oh_irs_gross_income(Variable):
    value_type = float
    entity = Person
    label = "Ohio gross income for the joint filing credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OH
    reference = "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=20"

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.gross_income
        total = 0
        not_dependent = ~person("is_tax_unit_dependent", period)
        sources = [
            source
            for source in p.sources
            if source
            not in [
                "taxable_interest_income",
                "dividend_income",
                "capital_gains",
                "rental_income",
            ]
        ]
        for source in sources:
            # Add positive values only - losses are deducted later.
            total += not_dependent * max_(0, add(person, period, [source]))
        return total
