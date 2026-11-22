from policyengine_us.model_api import *


class ct_temporary_premium_assistance_enhanced_ptc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut Temporary Premium Assistance enhanced premium tax credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT
    reference = (
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title26/pdf/USCODE-2024-title26-subtitleA-chap1-subchapA-partIV-subpartC-sec36B.pdf#page=2",
        "https://www.accesshealthct.com/article/active/new-financial-help-could-lower-your-health-coverage-costs-in-2026/",
        "https://www.accesshealthct.com/federal-changes-to-health-coverage/",
    )
    documentation = (
        "The premium tax credit the tax unit would get if the enhanced "
        "federal credit had not expired: the annual benchmark silver-plan "
        "premium for the coverage family (aca_ptc_slcsp) less the enhanced "
        "applicable percentage times household income, floored at zero. "
        "Access Health CT replaces 'the difference between the enhanced "
        "federal tax credit amounts (which expired at the end of 2025) and "
        "the current federal tax credit amounts'. No published worksheet "
        "says how that counterfactual credit is computed; this assumes the "
        "statutory 2021-2025 table against the same current-year benchmark "
        "that the current federal credit (aca_ptc) uses, so the two credits "
        "differ only by their applicable percentages."
    )

    def formula(tax_unit, period, parameters):
        # The benchmark for the federal coverage family, a MONTH variable
        # that add() sums over the year to match the YEAR-period aca_ptc.
        benchmark = add(tax_unit, period, ["aca_ptc_slcsp"])
        income = max_(tax_unit("aca_magi", period), 0)
        percentage = tax_unit(
            "ct_temporary_premium_assistance_enhanced_contribution_percentage",
            period,
        )
        return max_(0, benchmark - percentage * income)
