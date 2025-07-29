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
        # Map 'head' parameter key to 'head_of_household' for the utility
        param_dict = {
            "single": p.single,
            "separate": p.separate,
            "joint": p.joint,
            "head_of_household": p.head,
            "surviving_spouse": p.surviving_spouse,
        }
        return select_filing_status_value(
            filing_status, param_dict, agi, right=True
        )
