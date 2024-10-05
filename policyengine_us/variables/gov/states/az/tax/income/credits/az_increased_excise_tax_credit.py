from policyengine_us.model_api import *


class az_increased_excise_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Increased Excise Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = "az_increased_excise_tax_credit_eligible"
    reference = "https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01072-01.htm"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.az.tax.income.credits.increased_excise
        # The increased excise tax credit is allowed for each person that a
        # personal or dependent exemption can be claimed for
        tax_unit_size = tax_unit("tax_unit_size", period)
        uncapped_credit = tax_unit_size * p.amount
        return min_(uncapped_credit, p.max_amount)
