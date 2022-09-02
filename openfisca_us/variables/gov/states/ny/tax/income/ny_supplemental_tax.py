from openfisca_us.model_api import *


class ny_supplemental_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY supplemental income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        ny_taxable_income = tax_unit("ny_taxable_income", period)
        ny_agi = tax_unit("ny_agi", period)
        sup_tax = parameters(period).gov.states.ny.tax.income.supplemental

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

        recap_base = sup_tax.recapture_base
        single = recap_base.single
        joint = recap_base.joint
        hoh = recap_base.head_of_household
        widow = recap_base.widow
        separate = recap_base.separate
        scales = [single, joint, hoh, widow, separate]

        recapture_base = select(
            in_each_status,
            [scale.calc(ny_taxable_income) for scale in scales],
        )

        previous_threshold = select(
            in_each_status,
            [
                get_previous_threshold(ny_taxable_income, scale.thresholds)
                for scale in scales
            ],
        )

        next_threshold = select(
            in_each_status,
            [
                get_next_threshold(ny_taxable_income, scale.thresholds)
                for scale in scales
            ],
        )

        incremental_benefit = select(
            in_each_status,
            [
                scale.calc(next_threshold + 1) - recapture_base
                for scale in scales
            ],
        )

        applicable_amount = ny_agi - max_(previous_threshold, sup_tax.min_agi)

        phase_in_fraction = min_(
            1,
            applicable_amount / sup_tax.phase_in_length,
        )

        over_max_agi = ny_agi > sup_tax.agi_limit.max
        main_tax = tax_unit("ny_main_income_tax", period)
        target_tax_if_over_max_agi = (
            ny_taxable_income * sup_tax.agi_limit.tax_rate
        )

        return where(
            over_max_agi,
            target_tax_if_over_max_agi - main_tax,
            recapture_base + incremental_benefit * phase_in_fraction,
        )
