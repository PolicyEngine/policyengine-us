from policyengine_us.model_api import *


class de_tax_liability_if_refundable_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware tax liability if refudnable EITC"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        simulation = tax_unit.simulation
        refudable_branch = simulation.get_branch("de_refudable_eitc")
        refudable_branch.set_input(
            "de_tax_unit_eitc_refundable",
            period,
            np.ones((tax_unit.count,), dtype=bool),
        )
        return refudable_branch.calculate("de_income_tax", period)
