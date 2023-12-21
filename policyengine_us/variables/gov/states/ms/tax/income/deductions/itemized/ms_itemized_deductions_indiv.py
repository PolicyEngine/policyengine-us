from policyengine_us.model_api import *


class ms_itemized_deductions_indiv(Variable):
    value_type = float
    entity = Person
    label = "Mississippi itemized deductions when married couples file separately"
    unit = USD
    definition_period = YEAR

    reference = (
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=15"
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80108228.pdf, # Line 7"
        "https://casetext.com/statute/mississippi-code-1972/title-27-taxation-and-finance/chapter-7-income-tax-and-withholding/article-1-income-tax/section-27-7-17-deductions-allowed?__cf_chl_rt_tk=8Kelu8kHpIXTp_FnAJLHvqa7rtrZYE1U.NAeBM8L.Nc-1692990420-0-gaNycGzNEmU"
    )
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        total_itemized_deductions = person.tax_unit(
            "ms_itemized_deductions_joint", period
        )

        # Per the atx form, the exemption amount is split in half between the head
        # and the spouse of the household
        return head_or_spouse * (0.5 * itemized_exemptions)
