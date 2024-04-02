from policyengine_us.model_api import *


class ms_itemized_deductions_indiv(Variable):
    value_type = float
    entity = Person
    label = "Mississippi itemized deductions for individual couples"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=15"
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80108228.pdf, # Line 7"
        "https://casetext.com/statute/mississippi-code-1972/title-27-taxation-and-finance/chapter-7-income-tax-and-withholding/article-1-income-tax/section-27-7-17-deductions-allowed?__cf_chl_rt_tk=8Kelu8kHpIXTp_FnAJLHvqa7rtrZYE1U.NAeBM8L.Nc-1692990420-0-gaNycGzNEmU"
    )
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        unit_deds = person.tax_unit("ms_itemized_deductions_unit", period)
        return unit_deds * person("ms_prorate_fraction", period)
