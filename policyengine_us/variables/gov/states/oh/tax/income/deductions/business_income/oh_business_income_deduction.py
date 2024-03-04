from policyengine_us.model_api import *


class oh_business_income_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio business income deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/ohio/2022/title-57/chapter-5747/section-5747-01/",
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=10",
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        # Ohio can deduct a certain amount of their business income
        # included in federal AGI after the QBI deduction.
        p_irs = parameters(period).gov.irs.deductions.qbi
        income_components = add(tax_unit, period, p_irs.income_definition)
        fed_deduction = tax_unit("qualified_business_income_deduction", period)
        p = parameters(
            period
        ).gov.states.oh.tax.income.deductions.business_income
        reduced_income_components = max_(0, income_components - fed_deduction)
        filing_status = tax_unit("filing_status", period)
        return min_(reduced_income_components, p.cap[filing_status])
