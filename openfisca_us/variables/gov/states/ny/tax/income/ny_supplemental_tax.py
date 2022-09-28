from openfisca_us.model_api import *
<<<<<<< HEAD
=======
from openfisca_core.taxscales import MarginalRateTaxScale
>>>>>>> 32731216fc851e6adc043ee79ded21fad318b131


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
<<<<<<< HEAD
        sup_tax = parameters(period).gov.states.ny.tax.income.supplemental
=======
        tax = parameters(period).gov.states.ny.tax.income
        sup_tax = tax.supplemental
>>>>>>> 32731216fc851e6adc043ee79ded21fad318b131

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

<<<<<<< HEAD
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
=======
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
>>>>>>> 32731216fc851e6adc043ee79ded21fad318b131
                for scale in scales
            ],
        )

<<<<<<< HEAD
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

=======
        applicable_amount = max_(
            0, ny_agi - max_(previous_agi_threshold, sup_tax.min_agi)
        )

>>>>>>> 32731216fc851e6adc043ee79ded21fad318b131
        phase_in_fraction = min_(
            1,
            applicable_amount / sup_tax.phase_in_length,
        )

<<<<<<< HEAD
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
=======
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
>>>>>>> 32731216fc851e6adc043ee79ded21fad318b131
