from policyengine_us.model_api import *


class ny_agi_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY AGI additions"
    unit = USD
    documentation = "Additions to NY AGI over federal AGI."
    definition_period = YEAR
    dict(
        title="N.Y. Comp. Codes R. & Regs. tit. 20 § 112.2",
        href="https://casetext.com/regulation/new-york-codes-rules-and-regulations/title-20-department-of-taxation-and-finance/chapter-ii-income-taxes-and-estate-taxes/subchapter-a-new-york-state-personal-income-tax-under-article-22-of-the-tax-law/article-2-residents/part-112-new-york-adjusted-gross-income-of-a-resident-individual/section-1122-modifications-increasing-federal-adjusted-gross-income",
    )

    # No additions modeled in OpenFisca US.
