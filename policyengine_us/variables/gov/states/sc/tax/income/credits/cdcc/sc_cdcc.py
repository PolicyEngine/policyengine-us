from policyengine_us.model_api import *


class sc_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina CDCC"
    documentation = "South Carolina Child and Dependent Care Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.sc.gov/forms-site/Forms/IITPacket_2022.pdf#page=22"
    )
    defined_for = StateCode.SC

    def formula(tax_unit, period, parameters):
        # Get South Carolina CDCC rate.
        p_sc = parameters(period).gov.states.sc.tax.income.credits.cdcc
        p_us = parameters(period).gov.irs.credits.cdcc

        # Year 2021 is different from federal cdcc
        max_decoupled_year_offset = p_sc.max_care_expense_year_offset
        period_max = period.offset(max_decoupled_year_offset)
        sc_max_care_expense = parameters(period_max).gov.irs.credits.cdcc.max

        # Get child care expenses.
        childcare_expenses = tax_unit("tax_unit_childcare_expenses", period)

        # Married filing separate are ineligible.
        filing_status = tax_unit("filing_status", period)
        eligible = filing_status != filing_status.possible_values.SEPARATE

        # Number of qualifying people
        count_cdcc_eligible = min_(
            tax_unit("count_cdcc_eligible", period), p_us.eligibility.max
        )
        # Maximum value cannot exceed cap
        # Calculate total CDCC
        capped_expenses = min_(
            childcare_expenses, sc_max_care_expense * count_cdcc_eligible
        )
        return eligible * capped_expenses * p_sc.rate
