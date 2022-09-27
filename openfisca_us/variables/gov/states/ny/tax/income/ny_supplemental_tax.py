from openfisca_us.model_api import *
from openfisca_core.taxscales import MarginalRateTaxScale


class ny_supplemental_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY supplemental income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY

    def formula_2022(tax_unit, period, parameters):
        ny_taxable_income = tax_unit("ny_taxable_income", period)
        ny_agi = tax_unit("ny_agi", period)
        tax = parameters(period).gov.states.ny.tax.income
        sup_tax = tax.supplemental

        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        statuses = [
            status.SINGLE,
            status.JOINT,
            status.HEAD_OF_HOUSEHOLD,
            status.WIDOW,
            status.SEPARATE,
        ]
        in_each_status = [filing_status == s for s in statuses]

        rates = tax.main
        single = rates.single
        joint = rates.joint
        hoh = rates.head_of_household
        widow = rates.widow
        separate = rates.separate
        scales = [single, joint, hoh, widow, separate]

        previous_agi_threshold = select(
            in_each_status,
            [
                get_previous_threshold(ny_agi, scale.thresholds)
                for scale in scales
            ],
        )

        applicable_amount = max_(
            0, ny_agi - max_(previous_agi_threshold, sup_tax.min_agi)
        )

        phase_in_fraction = min_(
            1,
            applicable_amount / sup_tax.phase_in_length,
        )

        rate = select(
            in_each_status,
            [
                scale.marginal_rates(
                    max_(sup_tax.min_agi + 1, ny_taxable_income)
                )
                for scale in scales
            ],
        )

        target_tax = rate * ny_taxable_income
        difference = target_tax - tax_unit("ny_main_income_tax", period)
        return phase_in_fraction * difference
