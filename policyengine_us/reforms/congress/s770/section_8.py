"""Independent S.770 section 8 options; see README.md for scope and accounting."""

import numpy as np

from policyengine_us.model_api import *


def enabled(part, period):
    return part.in_effect and period.start.year >= part.start_year


def active_residual(total, passive, already_se, draw_exclusion=0):
    """Signed profits, assuming the passive and already-SE subsets are disjoint."""
    return total - passive - already_se - draw_exclusion


def allocate_bases(nii, active, excess):
    """Net signed sources before clipping, then allocate the limit to NII first."""
    limited = np.minimum(np.maximum(nii + active, 0), np.maximum(excess, 0))
    nii_base = np.minimum(np.maximum(nii, 0), limited)
    return nii_base, limited - nii_base


def transfer_shares(
    mode,
    existing_rate,
    addon_rate,
    active_rate,
    nii_share,
    active_share,
    bill_share,
    oasdi_rate,
):
    """Shares of existing NIIT, the add-on, and active tax, respectively."""
    # Core parameters accept numbers, booleans and lists, not string scalars.
    mode = {0: "custom", 1: "combined_rate_share", 2: "all_addon", 3: "bill"}.get(
        mode, mode
    )
    if mode == "custom":
        return 0, nii_share, active_share
    if mode == "bill":
        return bill_share, bill_share, bill_share
    if mode == "all_addon":
        return 0, 1, active_share
    if mode == "combined_rate_share":
        combined = existing_rate + addon_rate
        # With no NII add-on, this custom mode transfers no old-law NII
        # receipts. The independently enabled active option still transfers.
        nii = oasdi_rate / combined if addon_rate and combined else 0
        active = oasdi_rate / active_rate if active_rate else 0
        if not (0 <= nii <= 1 and 0 <= active <= 1):
            raise ValueError("OASDI rate must not exceed an enabled combined tax rate")
        return nii, nii, active
    raise ValueError(f"Unknown S.770 transfer mode: {mode}")


def revenue_shares(parameters, period):
    p = parameters(period).gov.contrib.congress.s770.section_8
    if period.start.year < p.transfer.start_year:
        return 0, 0, 0
    nii_on = enabled(p.nii_addon, period)
    active_on = enabled(p.active_business, period)
    if not (nii_on or active_on):
        return 0, 0, 0
    existing_rate = parameters(period).gov.irs.investment.net_investment_income_tax.rate
    return transfer_shares(
        p.transfer.mode,
        existing_rate,
        p.nii_addon.rate if nii_on else 0,
        p.active_business.rate if active_on else 0,
        p.nii_addon.oasdi_share,
        p.active_business.oasdi_share,
        p.transfer.bill_share,
        p.transfer.oasdi_rate,
    )


def create_s770_section_8():
    class net_investment_income_tax(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "Net investment income tax including enabled S.770 section 8 options"
        unit = USD
        reference = "https://www.congress.gov/bill/119th-congress/senate-bill/770/text"
        documentation = (
            "Entire resulting section 1411 liability, including the existing rate. "
            "When the active option is enabled, signed active losses also change "
            "the existing NIIT base. The named S.770 component taxes are already "
            "included here and must not be added to income tax a second time."
        )

        def formula(tax_unit, period, parameters):
            return add(
                tax_unit,
                period,
                [
                    "s770_existing_niit_tax",
                    "s770_nii_addon_tax",
                    "s770_active_business_income_tax",
                ],
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(net_investment_income_tax)

    return reform


def create_s770_section_8_reform(parameters, period, bypass=False):
    if bypass:
        return create_s770_section_8()
    p = parameters.gov.contrib.congress.s770.section_8
    # Install once if enabled anywhere in the parameter history. Formula gates
    # retain both independent start years, including requests in another order.
    if any(
        value.value
        for part in (p.nii_addon, p.active_business)
        for value in part.in_effect.values_list
    ):
        return create_s770_section_8()
    return None


section_8 = create_s770_section_8_reform(None, None, bypass=True)
