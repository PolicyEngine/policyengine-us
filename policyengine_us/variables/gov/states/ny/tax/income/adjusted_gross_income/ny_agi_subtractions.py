from policyengine_us.model_api import *


class ny_agi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York AGI subtractions"
    unit = USD
    documentation = "Subtractions from NY AGI over federal AGI."
    definition_period = YEAR
    dict(
        title="N.Y. Comp. Codes R. & Regs. tit. 20 § 112.3",
        href="https://casetext.com/regulation/new-york-codes-rules-and-regulations/title-20-department-of-taxation-and-finance/chapter-ii-income-taxes-and-estate-taxes/subchapter-a-new-york-state-personal-income-tax-under-article-22-of-the-tax-law/article-2-residents/part-112-new-york-adjusted-gross-income-of-a-resident-individual/section-1123-modifications-reducing-federal-adjusted-gross-income",
    )
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        # Get the list of subtractions from the YAML parameter
        subtractions_list = parameters(
            period
        ).gov.states.ny.tax.income.agi.subtractions.list

        # Dynamically sum all subtractions from the list
        return add(tax_unit, period, subtractions_list)
