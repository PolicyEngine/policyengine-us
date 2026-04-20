from policyengine_us.model_api import *


class nd_stillborn_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Dakota stillborn child deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ND
    reference = "https://ndlegis.gov/cencode/t57c38.pdf#nameddest=57-38-30p3"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.nd.tax.income.taxable_income.subtractions
        stillborn = tax_unit("tax_unit_stillborn_children", period)
        return stillborn * p.stillborn
