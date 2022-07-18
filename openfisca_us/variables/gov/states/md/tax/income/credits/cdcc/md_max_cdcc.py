from openfisca_us.model_api import *


class md_max_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD CDCC"
    documentation = "Maryland Child and Dependent Care Credit Maximum Amount"
    unit = USD
    definition_period = YEAR
    reference = "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-716-for-child-care-or-dependent-care"

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        agi = tax_unit("adjusted_gross_income", period)
        p = parameters(period).gov.states.md.tax.income.credits.cdcc
        # Eligibility is based on AGI.
        in_md = tax_unit.household("state_code_str", period) == "MD"
        eligible = (agi <= p.eligibility.agi_cap[filing_status]) & in_md
        # Maximum is a percent of federal.
        return p.percent * tax_unit("cdcc", period)
