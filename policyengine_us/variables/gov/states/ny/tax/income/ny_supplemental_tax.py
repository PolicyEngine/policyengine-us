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
                get_previous_threshold(ny_taxable_income, scale.thresholds)
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

        recapture_base = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.SEPARATE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.WIDOW,
            ],
            [
                sup_tax.recapture_base.single.calc(ny_taxable_income),
                sup_tax.recapture_base.separate.calc(ny_taxable_income),
                sup_tax.recapture_base.joint.calc(ny_taxable_income),
                sup_tax.recapture_base.head_of_household.calc(
                    ny_taxable_income
                ),
                sup_tax.recapture_base.widow.calc(ny_taxable_income),
            ],
        )

        incremental_benefit = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.SEPARATE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.WIDOW,
            ],
            [
                sup_tax.incremental_benefit.single.calc(ny_taxable_income),
                sup_tax.incremental_benefit.separate.calc(ny_taxable_income),
                sup_tax.incremental_benefit.joint.calc(ny_taxable_income),
                sup_tax.incremental_benefit.head_of_household.calc(
                    ny_taxable_income
                ),
                sup_tax.incremental_benefit.widow.calc(ny_taxable_income),
            ],
        )
        supplemental_tax_general = (
            recapture_base + phase_in_fraction * incremental_benefit
        )

        # edge case for low income
        min_taxable_income = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.SEPARATE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.WIDOW,
            ],
            [
                sup_tax.incremental_benefit.single.thresholds[0],
                sup_tax.incremental_benefit.separate.thresholds[0],
                sup_tax.incremental_benefit.joint.thresholds[0],
                sup_tax.incremental_benefit.head_of_household.thresholds[0],
                sup_tax.incremental_benefit.widow.thresholds[0],
            ],
        )
        low_income_rate = select(
            in_each_status,
            [scale.marginal_rates(min_taxable_income + 1) for scale in scales],
        )
        supplemental_tax_low_income = (
            ny_taxable_income * low_income_rate
            - phase_in_fraction * ny_main_income_tax
        )

        # edge case for high agi > $25,000,000 TODO: check length
        high_income_rate = select(
            in_each_status,
            [scale.marginal_rates(sup_tax.max_agi) for scale in scales],
        )

        # supplemental_tax_high_income = (
        #     ny_taxable_income * high_income_rate - ny_main_income_tax
        # )

        # supplemental_tax = select(
        #     [ny_taxable_income < min_taxable_income, ny_agi > max_agi],
        #     [supplemental_tax_low_income, supplemental_tax_high_income],
        #     default=supplemental_tax_general,
        # )

        return sup_tax.max_agi

        # rate = select(
        #     in_each_status,
        #     [
        #         scale.marginal_rates(
        #             max_(sup_tax.min_agi + 1, ny_taxable_income)
        #         )
        #         for scale in scales
        #     ],
        # )

        # target_tax = rate * ny_taxable_income
        # difference = target_tax - tax_unit("ny_main_income_tax", period)
        # return phase_in_fraction * difference
