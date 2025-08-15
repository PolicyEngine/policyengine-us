from policyengine_us.model_api import *
from policyengine_core.taxscales import MarginalRateTaxScale
from policyengine_us.tools.general import (
    select_filing_status_value,
    get_previous_threshold,
)


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

        # Create a dictionary for rate schedules
        rate_schedules = {
            "single": rates.single,
            "joint": rates.joint,
            "head_of_household": rates.head_of_household,
            "surviving_spouse": rates.surviving_spouse,
            "separate": rates.separate,
        }

        # Get previous AGI threshold based on filing status
        def get_previous_threshold_value(scale):
            return get_previous_threshold(ny_taxable_income, scale.thresholds)

        previous_agi_threshold = select_filing_status_value(
            filing_status,
            {
                k: get_previous_threshold_value(v)
                for k, v in rate_schedules.items()
            },
        )

        applicable_amount = max_(
            0, ny_agi - max_(previous_agi_threshold, p.min_agi)
        )

        phase_in_fraction = min_(
            1,
            applicable_amount / p.phase_in_length,
        )

        # edge case for high agi
        agi_limit = select_filing_status_value(
            filing_status,
            {k: v.thresholds[-1] for k, v in rate_schedules.items()},
        )

        high_agi_rate = select_filing_status_value(
            filing_status,
            {
                k: v.marginal_rates(agi_limit + 1)
                for k, v in rate_schedules.items()
            },
        )

        supplemental_tax_high_agi = (
            ny_taxable_income * high_agi_rate - ny_main_income_tax
        )

        if p.in_effect:
            recapture_base = select_filing_status_value(
                filing_status,
                p.recapture_base,
                ny_taxable_income,
            )

            incremental_benefit = select_filing_status_value(
                filing_status,
                p.incremental_benefit,
                ny_taxable_income,
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
