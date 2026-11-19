from policyengine_us.model_api import *


class ct_temporary_premium_assistance_enhanced_contribution_percentage(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut Temporary Premium Assistance enhanced applicable percentage"
    unit = "/1"
    definition_period = YEAR
    defined_for = StateCode.CT
    reference = (
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title26/pdf/USCODE-2024-title26-subtitleA-chap1-subchapA-partIV-subpartC-sec36B.pdf#page=2",
        "https://www.accesshealthct.com/article/active/new-financial-help-could-lower-your-health-coverage-costs-in-2026/",
    )
    documentation = (
        "The applicable percentage of the enhanced premium tax credit that "
        "expired at the end of 2025, from the 2021-2025 table of 26 U.S.C. "
        "36B(b)(3)(A)(iii): 0% up to 150% of the poverty line, rising "
        "linearly to 2% at 200%, 4% at 250%, 6% at 300% and 8.5% at 400%, "
        "and 8.5% above 400% with no income cap. Temporary Premium "
        "Assistance replaces all or half of the credit this percentage "
        "gives. The bracket position is read at aca_magi_fraction, the "
        "truncated percentage the current federal credit "
        "(aca_required_contribution_percentage) also uses, so the expired "
        "and current credits differ only by their tables."
    )

    def formula(tax_unit, period, parameters):
        magi_frac = tax_unit("aca_magi_fraction", period)
        p = parameters(
            period
        ).gov.states.ct.ahct.temporary_premium_assistance.enhanced_contribution_percentage

        thresholds = np.array(p.threshold)
        initial_rates = np.array(p.initial)
        final_rates = np.array(p.final)

        # The percentage slopes linearly within each band, which a scale
        # parameter cannot express, so look up the bracket and interpolate.
        # searchsorted returns the insertion index; subtract 1 for the
        # bracket index, clipped so bracket_idx + 1 is always a valid
        # threshold index.
        bracket_idx = clip(
            np.searchsorted(thresholds, magi_frac, side="right") - 1,
            0,
            len(initial_rates) - 1,
        )
        bracket_start = thresholds[bracket_idx]
        bracket_end = thresholds[bracket_idx + 1]
        # Income above the last threshold (400%) clips to the end of the
        # last bracket: the table's "400.0 percent and higher" row is 8.5%
        # throughout, and the expired credit had no income cap.
        position = clip(
            (magi_frac - bracket_start) / (bracket_end - bracket_start),
            0,
            1,
        )
        initial = initial_rates[bracket_idx]
        final = final_rates[bracket_idx]
        return initial + position * (final - initial)
