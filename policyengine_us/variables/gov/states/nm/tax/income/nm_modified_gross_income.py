from policyengine_us.model_api import *


class nm_modified_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico modified gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503656",
        "https://www.law.cornell.edu/regulations/new-mexico/N-M-Admin-Code-SS-3.3.1.10",
    )
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        # Per NM Admin Code 3.3.1.10:
        # "zero is the lowest amount which may be reported for any item
        # in computing 'modified gross income'"
        # "The loss from one business or activity shall not reduce
        # the income from another business or activity."
        sources = parameters(period).gov.states.nm.tax.income.modified_gross_income
        total = 0
        for source in sources:
            total += max_(add(tax_unit, period, [source]), 0)
        return total
