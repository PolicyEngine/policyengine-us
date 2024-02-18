from policyengine_us.model_api import *
from policyengine_core.taxscales import MarginalRateTaxScale


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
        ny_main_income_tax = tax_unit("ny_main_income_tax", period)
        tax = parameters(period).gov.states.ny.tax.income
        p = tax.supplemental

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
                get_previous_threshold(ny_taxable_income, scale.thresholds)
                for scale in scales
            ],
        )

        applicable_amount = max_(
            0, ny_agi - max_(previous_agi_threshold, p.min_agi)
        )

        phase_in_fraction = min_(
            1,
            applicable_amount / p.phase_in_length,
        )

        recapture_base = select(
            in_each_status,
            [
                p.recapture_base.single.calc(ny_taxable_income),
                p.recapture_base.joint.calc(ny_taxable_income),
                p.recapture_base.head_of_household.calc(ny_taxable_income),
                p.recapture_base.widow.calc(ny_taxable_income),
                p.recapture_base.separate.calc(ny_taxable_income),
            ],
        )

        incremental_benefit = select(
            in_each_status,
            [
                p.incremental_benefit.single.calc(ny_taxable_income),
                p.incremental_benefit.joint.calc(ny_taxable_income),
                p.incremental_benefit.head_of_household.calc(
                    ny_taxable_income
                ),
                p.incremental_benefit.widow.calc(ny_taxable_income),
                p.incremental_benefit.separate.calc(ny_taxable_income),
            ],
        )

        supplemental_tax_general = (
            recapture_base + phase_in_fraction * incremental_benefit
        )

        # edge case for high agi
        agi_limit = select(
            in_each_status,
            [
                single.thresholds[-1],
                joint.thresholds[-1],
                hoh.thresholds[-1],
                widow.thresholds[-1],
                separate.thresholds[-1],
            ],
        )
        high_agi_rate = select(
            in_each_status,
            [scale.marginal_rates(agi_limit + 1) for scale in scales],
        )

        supplemental_tax_high_agi = (
            ny_taxable_income * high_agi_rate - ny_main_income_tax
        )

        return where(
            ny_agi > agi_limit,
            supplemental_tax_high_agi,
            supplemental_tax_general,
        )
