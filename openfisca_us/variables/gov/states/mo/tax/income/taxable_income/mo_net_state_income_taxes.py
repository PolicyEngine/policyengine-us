from openfisca_us.model_api import *


class mo_net_state_income_taxes(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri net state income taxes"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.mo.gov/forms/MO-A_2021.pdf"

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        adjustment_base_amount = parameters(
            period
        ).gov.irs.deductions.itemized.salt_and_real_estate.cap[filing_status]

        # Taxes/income
        state_and_local_sales_or_income_tax = tax_unit(
            "state_and_local_sales_or_income_tax", period
        )
        state_and_local_income_tax = add(
            tax_unit, period, ["state_income_tax", "local_income_tax"]
        )
        # Defined as local income tax from the Federal W2 on page 26 here: https://dor.mo.gov/forms/MO-1040%20Instructions_2021.pdf
        earnings_tax = tax_unit("local_income_tax", period)

        # Logic here is redundant (local income tax is part of state_and_local_income_tax
        # as well as the entirety of earnings_tax, but I feel this represents the true logic better)
        net_state_income_taxes = state_and_local_income_tax - earnings_tax
        income_tax_to_total_ratio = (
            net_state_income_taxes / state_and_local_sales_or_income_tax
        )

        # The threshold is the same as the adjustment_base_amount, i.e. the SALT cap introduced by TCJA
        threshold = adjustment_base_amount

        return where(
            state_and_local_sales_or_income_tax > threshold,
            adjustment_base_amount * (income_tax_to_total_ratio),
            net_state_income_taxes,
        )
