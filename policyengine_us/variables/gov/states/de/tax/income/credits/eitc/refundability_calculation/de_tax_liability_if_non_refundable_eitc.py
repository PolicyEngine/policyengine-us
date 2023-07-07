from policyengine_us.model_api import *
from policyengine_core.tracers import SimpleTracer


class de_tax_liability_if_non_refundable_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware tax liability if non-refundbale EITC"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        simulation = tax_unit.simulation
        non_itemized_branch = simulation.get_branch("de_non_refudable_eitc")
        non_itemized_branch.set_input(
            "de_tax_unit_eitc_refundable",
            period,
            np.zeros((tax_unit.count,), dtype=bool),
        )
        return non_itemized_branch.calculate(
            "de_income_tax", period
        )