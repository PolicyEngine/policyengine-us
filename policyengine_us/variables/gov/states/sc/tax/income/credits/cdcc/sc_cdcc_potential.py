from policyengine_us.model_api import *


class sc_cdcc_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina CDCC"
    documentation = "South Carolina Child and Dependent Care Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.scstatehouse.gov/code/t12c006.php",  # S.C. Code § 12-6-3380
        "https://dor.sc.gov/forms-site/Forms/IITPacket_2022.pdf#page=22",
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
        childcare_expenses = tax_unit("cdcc_relevant_expenses", period)

        # S.C. Code Ann. § 12-6-3380 computes the credit "as provided in
        # Internal Revenue Code Section 21," importing § 21 wholesale with only
        # the applicable-percentage (7%) and SC-source-income modifications. It
        # adds no filing-status language of its own, so it carries the
        # § 21(e)(2) joint-return requirement together with the § 21(e)(4)
        # separated-taxpayer exception. A married-separate filer who lives apart
        # while maintaining a home for a qualifying individual is therefore
        # eligible, matching the federal treatment; an ordinary MFS filer
        # remains ineligible.
        eligible = tax_unit("cdcc_filing_status_eligible", period)

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
