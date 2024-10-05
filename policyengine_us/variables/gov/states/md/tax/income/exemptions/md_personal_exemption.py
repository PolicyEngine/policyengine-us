from policyengine_us.model_api import *


class md_personal_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD value per personal exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD
    reference = "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-2-maryland-taxable-income-calculations-for-individual/part-iii-exemptions/section-10-211-individuals-other-than-fiduciaries?searchWithin=true&listingIndexId=code-of-maryland.article-tax-general&q=blind&type=statute&sort=relevance&p=1"

    def formula(tax_unit, period, parameters):
        # Get filing status and AGI.
        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        agi = tax_unit("adjusted_gross_income", period)
        # Calculate for each filing status depending on AGI.
        p = parameters(period).gov.states.md.tax.income.exemptions.personal
        return select(
            [
                filing_status == filing_statuses.SINGLE,
                filing_status == filing_statuses.SEPARATE,
                filing_status == filing_statuses.JOINT,
                filing_status == filing_statuses.HEAD_OF_HOUSEHOLD,
                filing_status == filing_statuses.SURVIVING_SPOUSE,
            ],
            [
                p.single.calc(agi, right=True),
                p.separate.calc(agi, right=True),
                p.joint.calc(agi, right=True),
                p.head.calc(agi, right=True),
                p.widow.calc(agi, right=True),
            ],
        )
