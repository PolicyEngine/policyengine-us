from policyengine_us.model_api import *


class co_pension_subtraction_indv_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Colorado pension and annuity subtraction for eligible individuals"
    defined_for = StateCode.CO
    reference = (
        "https://tax.colorado.gov/sites/tax/files/documents/DR0104AD_2022.pdf#page=1",
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=12",
        "https://law.justia.com/codes/colorado/2022/title-39/article-22/part-1/section-39-22-104/",
        # C.R.S. 39-22-104(4)(g)(III)
    )
    definition_period = YEAR

    def formula(person, period, parameters):
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        return head | spouse
