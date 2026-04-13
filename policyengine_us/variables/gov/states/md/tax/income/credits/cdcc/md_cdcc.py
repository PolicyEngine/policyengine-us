from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class md_cdcc_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD CDCC"
    documentation = "Maryland Child and Dependent Care Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-716-for-child-care-or-dependent-care"
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        agi = tax_unit("adjusted_gross_income", period)
        p = parameters(period).gov.states.md.tax.income.credits.cdcc
        # Eligibility is based on AGI.
        eligible = agi <= p.eligibility.agi_cap[filing_status]
        # Maximum is a percent of federal.
        # Maryland matches the federal credit allowed (after Credit Limit Worksheet)
        max_cdcc = p.percent * tax_unit("cdcc", period)
        # Phases out based on filing status.
        phase_out_start = p.phase_out.start[filing_status]
        excess = max_(0, agi - phase_out_start)
        phase_out_increment = p.phase_out.increment[filing_status]
        phase_out_increments = np.ceil(excess / phase_out_increment)
        percent_reduction = phase_out_increments * p.phase_out.percent
        return eligible * max_(0, max_cdcc * (1 - percent_reduction))


class md_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD CDCC"
    documentation = "Maryland Child and Dependent Care Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-716-for-child-care-or-dependent-care"
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.md.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "md_income_tax_before_credits",
            "md_cdcc",
            "md_cdcc_potential",
        )
