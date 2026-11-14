from policyengine_us.model_api import *


class mn_homestead_credit_refund(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota Homestead Credit Refund"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290A.04",
        "https://www.taxformfinder.org/forms/2024/2024-minnesota-form-m1pr-instructions.pdf#page=23",
        "https://www.taxformfinder.org/forms/2025/2025-minnesota-form-m1pr-instructions.pdf#page=23",
        "https://www.revisor.mn.gov/laws/2026/0/128/",
        # PDF pages 5, 9, 14-23.
        "https://www.revenue.state.mn.us/sites/default/files/2026-06/m1pr-inst-25.pdf#page=5",
        "https://www.revenue.state.mn.us/sites/default/files/2026-06/m1pr-25.pdf#page=2",
    )
    defined_for = "mn_homestead_credit_refund_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.property.homestead_credit_refund
        household_income = max_(
            0, tax_unit("mn_homestead_credit_refund_household_income", period)
        )
        property_tax = add(tax_unit, period, ["real_estate_taxes"])
        excess_property_tax = max_(
            0,
            property_tax
            - household_income * p.percent_of_income.calc(household_income),
        )
        refund = excess_property_tax * p.refund_rate.calc(household_income)
        base_refund = round_(min_(refund, p.max_refund.calc(household_income)))
        additional_refund = round_(base_refund * p.one_time_additional_refund_rate)
        return base_refund + additional_refund

    def formula_2025(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.property.homestead_credit_refund
        household_income = np.floor(
            max_(0, tax_unit("mn_homestead_credit_refund_household_income", period))
            + 0.5
        )
        qualified_tax = np.floor(
            tax_unit("mn_homestead_credit_refund_qualified_property_taxes", period)
            + 0.5
        )
        special_refund = tax_unit("mn_special_refund", period)
        property_tax = max_(qualified_tax - special_refund, 0)

        table_income = p.table_income_midpoint.calc(household_income)
        table_tax = (
            np.floor(property_tax / p.table_tax_band_width) + 0.5
        ) * p.table_tax_band_width
        table_excess = max_(
            table_tax - table_income * p.percent_of_income.calc(table_income), 0
        )
        table_refund = np.floor(
            min_(
                table_excess * p.refund_rate.calc(table_income),
                p.max_refund.calc(table_income),
            )
            + 0.5
        )

        required_contribution = np.floor(
            household_income * p.percent_of_income.calc(household_income) + 0.5
        )
        worksheet_excess = max_(property_tax - required_contribution, 0)
        worksheet_refund = min_(
            np.floor(worksheet_excess * p.refund_rate.calc(household_income) + 0.5),
            p.max_refund.calc(household_income),
        )
        base_refund = where(
            property_tax > 0,
            where(property_tax < p.table_tax_ceiling, table_refund, worksheet_refund),
            0,
        )
        additional_refund = np.floor(
            base_refund * p.one_time_additional_refund_rate + 0.5
        )
        return base_refund + additional_refund
