from policyengine_us.model_api import *


class id_income_tax_if_receiving_aged_or_disabled_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "Idaho income tax if claiming the aged or disabled deduction over the credit"
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        simulation = tax_unit.simulation
        branch = simulation.get_branch("id_receives_aged_or_disabled_deduction_branch")
        branch.set_input(
            "id_receives_aged_or_disabled_credit",
            period,
            np.zeros((tax_unit.count,), dtype=bool),
        )
        return branch.calculate("id_income_tax", period)
