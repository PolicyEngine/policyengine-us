from policyengine_us.model_api import *


class de_income_tax_if_claiming_refundable_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware tax liability if claiming refundable Delaware EITC"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        simulation = tax_unit.simulation
        refundable_branch = get_override_branch(
            simulation,
            "de_refundable_eitc",
            period,
            {"de_claims_refundable_eitc": np.ones((tax_unit.count,), dtype=bool)},
        )
        return refundable_branch.calculate("de_income_tax", period)
