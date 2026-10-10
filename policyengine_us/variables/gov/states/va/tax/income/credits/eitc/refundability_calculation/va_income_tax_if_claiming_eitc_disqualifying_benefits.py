from policyengine_us.model_api import *


class va_income_tax_if_claiming_eitc_disqualifying_benefits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia tax liability if claiming the benefits that bar the Virginia EITC"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        simulation = tax_unit.simulation
        # Each Virginia choice branch fixes both choices, so no branch
        # creates branches of its own. Claiming a listed benefit bars every
        # credit in Va. Code 58.1-339.8, which makes the form of the EITC moot.
        benefits_branch = get_override_branch(
            simulation,
            "va_eitc_disqualifying_benefits",
            period,
            {
                "va_claims_eitc_disqualifying_benefits": np.ones(
                    (tax_unit.count,), dtype=bool
                ),
                "va_claims_refundable_eitc": np.zeros((tax_unit.count,), dtype=bool),
            },
        )
        return benefits_branch.calculate("va_income_tax", period)
