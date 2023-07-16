from policyengine_us.model_api import *


class de_income_tax_if_claiming_non_refundable_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware tax liability if claiming non-refundable Delaware EITC"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        simulation = tax_unit.simulation
        non_refundable_branch = simulation.get_branch("de_non_refundable_eitc")
        non_refundable_branch.set_input(
            "de_claims_refundable_eitc",
            period,
            np.zeros((tax_unit.count,), dtype=bool),
        )
        return non_refundable_branch.calculate("de_income_tax", period)
