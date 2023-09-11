from policyengine_us.model_api import *


class az_net_capital_gains_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona net capital gains subtractions"
    unit = USD
    documentation = "https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01022.htm"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.az.tax.income.deductions.net_capital_gains
        person = tax_unit.members

        net_cg_subtraction = tax_unit("net_capital_gain", period)

        long_term_capital_gains = person("long_term_capital_gains", period)
        long_term_cg_subtraction = long_term_capital_gains * p.subtraction_rate

        return net_cg_subtraction + long_term_cg_subtraction
