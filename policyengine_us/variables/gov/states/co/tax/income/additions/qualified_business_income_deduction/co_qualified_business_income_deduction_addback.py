from policyengine_us.model_api import *


class co_qualified_business_income_deduction_addback(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado qualified business income deduction addback"
    unit = USD
    definition_period = YEAR
    reference = (
        # C.R.S. 39-22-104 . Income tax imposed on individuals, estates, and trusts - section (3) (o)
        "https://casetext.com/statute/colorado-revised-statutes/title-39-taxation/specific-taxes/income-tax/article-22-income-tax/part-1-general/section-39-22-104-effective-until-official-proclamation-by-governor-income-tax-imposed-on-individuals-estates-and-trusts-single-rate-report-legislative-declaration-definitions-repeal",
        # 2022 Colorado Individual Income Tax Filing Guide - Additions
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=5",
        # 2021 Colorado Individual Income Tax Filing Guide - Additions
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2021.pdf#page=5",
        # Individual Income Tax Guide - Part 3 Additions to Taxable Income
        "https://tax.colorado.gov/individual-income-tax-guide",
    )
    defined_for = "co_qualified_business_income_deduction_addback_required"

    adds = ["qualified_business_income_deduction"]
