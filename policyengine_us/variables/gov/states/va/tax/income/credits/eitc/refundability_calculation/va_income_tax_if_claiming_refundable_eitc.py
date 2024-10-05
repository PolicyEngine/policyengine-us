from policyengine_us.model_api import *


class va_income_tax_if_claiming_refundable_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia tax liability if claiming refundable Virginia EITC"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        simulation = tax_unit.simulation
        refundable_branch = simulation.get_branch("va_refundable_eitc")
        refundable_branch.set_input(
            "va_claims_refundable_eitc",
            period,
            np.ones((tax_unit.count,), dtype=bool),
        )
        return refundable_branch.calculate("va_income_tax", period)
