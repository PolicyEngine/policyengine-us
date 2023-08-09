from policyengine_us.model_api import *


class va_income_tax_if_claiming_non_refundable_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia tax liability if claiming non-refundable Virginia EITC"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        simulation = tax_unit.simulation
        non_refundable_branch = simulation.get_branch("va_non_refundable_eitc")
        non_refundable_branch.set_input(
            "va_claims_refundable_eitc",
            period,
            np.zeros((tax_unit.count,), dtype=bool),
        )
        return non_refundable_branch.calculate("va_income_tax", period)
