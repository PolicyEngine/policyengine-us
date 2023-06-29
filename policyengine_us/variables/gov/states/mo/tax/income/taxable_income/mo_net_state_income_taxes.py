from policyengine_us.model_api import *


class mo_net_state_income_taxes(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri net state income taxes"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-A_2021.pdf",
        "https://revisor.mo.gov/main/OneSection.aspx?section=143.141&bid=7212",
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        adjustment_base_amount = parameters(
            period
        ).gov.irs.deductions.itemized.salt_and_real_estate.cap[filing_status]

        # Taxes/income
        state_and_local_sales_or_income_tax = tax_unit(
            "state_and_local_sales_or_income_tax", period
        )

        # Technically, state and local income tax could include the
        # "local_earnings_tax" variable,
        # but because the definition of net_state_income_taxes is
        # simply (state_tax + local_tax) - local_tax,
        # it is redundant to keep it
        # More info about local income tax from the Federal W2 on page 26 here:
        # https://dor.mo.gov/forms/MO-1040%20Instructions_2021.pdf

        net_state_income_taxes = tax_unit("state_income_tax", period)
        # Compute the share of SALT from net state income taxes.
        # Use a mask rather than where to avoid a divide-by-zero warning. Default to one.
        tax_ratio = np.ones_like(net_state_income_taxes)
        mask = state_and_local_sales_or_income_tax != 0
        tax_ratio[mask] = (
            net_state_income_taxes[mask]
            / state_and_local_sales_or_income_tax[mask]
        )

        # The threshold is the same as the adjustment_base_amount,
        # i.e. the SALT cap introduced by TCJA
        threshold = adjustment_base_amount

        return where(
            state_and_local_sales_or_income_tax > threshold,
            adjustment_base_amount * tax_ratio,
            net_state_income_taxes,
        )
