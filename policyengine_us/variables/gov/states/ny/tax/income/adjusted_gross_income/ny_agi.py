from policyengine_us.model_api import *


class ny_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = "https://casetext.com/regulation/new-york-codes-rules-and-regulations/title-20-department-of-taxation-and-finance/chapter-ii-income-taxes-and-estate-taxes/subchapter-a-new-york-state-personal-income-tax-under-article-22-of-the-tax-law/article-3-nonresidents/part-132-new-york-adjusted-gross-income-of-a-nonresident-individual/new-york-adjusted-gross-income-defined/section-1321-new-york-adjusted-gross-income-of-a-nonresident-individual"
    defined_for = StateCode.NY

    adds = ["adjusted_gross_income", "ny_additions"]
    subtracts = ["ny_agi_subtractions"]
