from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    ordered_capped_state_non_refundable_credits,
)


def create_oh_refundable_eitc() -> Reform:
    """
    Ohio Refundable EITC Reform

    Hypothetical reform that pays the Ohio EITC as a fully refundable
    credit. ORC § 5747.71 currently makes the credit nonrefundable; this
    contrib module is used for what-if analysis only and does not reflect
    enacted Ohio law.

    Reading ``oh_eitc_potential`` (uncapped 30% of the federal EITC) yields
    the full refundable amount for the modeled era (2020+): Ohio's pre-2019
    "50% of tax when OH taxable income exceeds $20,000" limitation was
    repealed by HB 62 (eff. 2019-07-03), so the only remaining limit on the
    nonrefundable ``oh_eitc`` is the ordinary tax-liability cap — exactly
    what refundability lifts.
    https://codes.ohio.gov/ohio-revised-code/section-5747.71
    """

    class oh_refundable_eitc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Ohio refundable Earned Income Credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.OH

        def formula(tax_unit, period, parameters):
            # Use the potential (uncapped) OH EITC so the full credit is paid
            # as a refund; `oh_eitc` is capped at remaining tax liability via
            # the ordered nonrefundable cap and would zero out the credit for
            # the low-liability filers refundability is meant to help.
            return tax_unit("oh_eitc_potential", period)

    class oh_non_refundable_eitc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Ohio nonrefundable Earned Income Credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.OH

        def formula(tax_unit, period, parameters):
            # Reform makes EITC fully refundable, so nonrefundable portion is 0
            return 0

    class oh_non_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Ohio non-refundable credits"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/sch-cre.pdf",
            "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/itschedule-credits.pdf",
            "https://dam.assets.ohio.gov/image/upload/tax.ohio.gov/forms/ohio_individual/individual/2023/1040-bundle-original.pdf#page=7",
            "https://tax.ohio.gov/static/webview/view1/UIExtension/1/pdf-view.html?filename=forms/ohio_individual/individual/2024/1040-bundle-original-fi.pdf",
            "https://dam.assets.ohio.gov/image/upload/v1767095693/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=28",
        )
        defined_for = StateCode.OH

        def formula(tax_unit, period, parameters):
            # Mirror the baseline's ordered-cap logic but drop oh_eitc from
            # the non-refundable bucket — it's paid as refundable under this
            # reform. The previous formula returned only oh_non_refundable_eitc
            # (= 0 under the reform), which silently zeroed out every other
            # entry in Ohio's ordered non-refundable list (CDCC, senior,
            # retirement, non-public school, exemption, joint filing — plus the
            # adoption credit for pre-2023 years).
            ordered_credits = parameters(
                period
            ).gov.states.oh.tax.income.credits.non_refundable
            filtered_credits = [
                credit for credit in list(ordered_credits) if credit != "oh_eitc"
            ]
            return ordered_capped_state_non_refundable_credits(
                tax_unit,
                period,
                filtered_credits,
                "oh_income_tax_before_non_refundable_credits",
            )

    class oh_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Ohio refundable credits"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/sch-cre.pdf",
            "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/itschedule-credits.pdf",
            "https://dam.assets.ohio.gov/image/upload/tax.ohio.gov/forms/ohio_individual/individual/2023/1040-bundle-original.pdf#page=7",
            "https://tax.ohio.gov/static/webview/view1/UIExtension/1/pdf-view.html?filename=forms/ohio_individual/individual/2024/1040-bundle-original-fi.pdf",
            "https://dam.assets.ohio.gov/image/upload/v1767095693/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=28",
        )
        defined_for = StateCode.OH

        def formula(tax_unit, period, parameters):
            # Add refundable EITC (positive when reform is in effect)
            return tax_unit("oh_refundable_eitc", period)

    class reform(Reform):
        def apply(self):
            self.update_variable(oh_refundable_eitc)
            self.update_variable(oh_non_refundable_eitc)
            self.update_variable(oh_non_refundable_credits)
            self.update_variable(oh_refundable_credits)

    return reform


def create_oh_refundable_eitc_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_oh_refundable_eitc()

    p = parameters.gov.contrib.states.oh.child_poverty_impact_dashboard.eitc

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_oh_refundable_eitc()
    else:
        return None


oh_refundable_eitc = create_oh_refundable_eitc_reform(None, None, bypass=True)
