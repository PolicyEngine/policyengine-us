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
        rates = tax.main
        single = rates.single
        joint = rates.joint
        hoh = rates.head_of_household
        surviving_spouse = rates.surviving_spouse
        separate = rates.separate

        previous_agi_threshold = select(
            [
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.SURVIVING_SPOUSE,
                filing_status == status.SEPARATE,
            ],
            [
                get_previous_threshold(ny_taxable_income, joint.thresholds),
                get_previous_threshold(ny_taxable_income, hoh.thresholds),
                get_previous_threshold(ny_taxable_income, surviving_spouse.thresholds),
                get_previous_threshold(ny_taxable_income, separate.thresholds),
            ],
            # Default covers SINGLE
            default=get_previous_threshold(ny_taxable_income, single.thresholds),
        )

        applicable_amount = max_(0, ny_agi - max_(previous_agi_threshold, p.min_agi))

        phase_in_fraction = min_(
            1,
            applicable_amount / p.phase_in_length,
        )

        # edge case for high agi
        agi_limit = select(
            [
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.SURVIVING_SPOUSE,
                filing_status == status.SEPARATE,
            ],
            [
                joint.thresholds[-1],
                hoh.thresholds[-1],
                surviving_spouse.thresholds[-1],
                separate.thresholds[-1],
            ],
            # Default covers SINGLE
            default=single.thresholds[-1],
        )
        scales = [single, joint, hoh, surviving_spouse, separate]
        high_agi_rate = select(
            [
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.SURVIVING_SPOUSE,
                filing_status == status.SEPARATE,
            ],
            [scale.marginal_rates(agi_limit + 1) for scale in scales[1:]],
            # Default covers SINGLE
            default=single.marginal_rates(agi_limit + 1),
        )

        supplemental_tax_high_agi = (
            ny_taxable_income * high_agi_rate - ny_main_income_tax
        )

        if p.in_effect:
            recapture_base = select(
                [
                    filing_status == status.JOINT,
                    filing_status == status.HEAD_OF_HOUSEHOLD,
                    filing_status == status.SURVIVING_SPOUSE,
                    filing_status == status.SEPARATE,
                ],
                [
                    p.recapture_base.joint.calc(ny_taxable_income),
                    p.recapture_base.head_of_household.calc(ny_taxable_income),
                    p.recapture_base.surviving_spouse.calc(ny_taxable_income),
                    p.recapture_base.separate.calc(ny_taxable_income),
                ],
                # Default covers SINGLE
                default=p.recapture_base.single.calc(ny_taxable_income),
            )

            incremental_benefit = select(
                [
                    filing_status == status.JOINT,
                    filing_status == status.HEAD_OF_HOUSEHOLD,
                    filing_status == status.SURVIVING_SPOUSE,
                    filing_status == status.SEPARATE,
                ],
                [
                    p.incremental_benefit.joint.calc(ny_taxable_income),
                    p.incremental_benefit.head_of_household.calc(ny_taxable_income),
                    p.incremental_benefit.surviving_spouse.calc(ny_taxable_income),
                    p.incremental_benefit.separate.calc(ny_taxable_income),
                ],
                # Default covers SINGLE
                default=p.incremental_benefit.single.calc(ny_taxable_income),
            )

            supplemental_tax_general = (
                recapture_base + phase_in_fraction * incremental_benefit
            )

            return where(
                ny_agi > agi_limit,
                supplemental_tax_high_agi,
                supplemental_tax_general,
            )

        return where(
            ny_agi > agi_limit,
            supplemental_tax_high_agi,
            0,
        )
