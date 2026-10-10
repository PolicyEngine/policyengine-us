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
        # Claiming a credit means forgoing the benefits that bar it (Va. Code
        # 58.1-339.8(D)); fixing both choices keeps this branch from creating
        # branches of its own.
        refundable_branch = get_override_branch(
            simulation,
            "va_refundable_eitc",
            period,
            {
                "va_claims_refundable_eitc": np.ones((tax_unit.count,), dtype=bool),
                "va_claims_eitc_disqualifying_benefits": np.zeros(
                    (tax_unit.count,), dtype=bool
                ),
            },
        )
        return refundable_branch.calculate("va_income_tax", period)
