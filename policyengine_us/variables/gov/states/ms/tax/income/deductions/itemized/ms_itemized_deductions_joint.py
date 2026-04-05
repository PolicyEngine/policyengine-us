from policyengine_us.model_api import *


class ms_itemized_deductions_joint(Variable):
    value_type = float
    entity = Person
    label = "Mississippi itemized deductions for joint couples"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=15",
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80108228.pdf",  # Line 7
        "https://law.justia.com/codes/mississippi/title-27/chapter-7/article-1/section-27-7-17/",  # MS Code 27-7-17
    )
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        deductions = person.tax_unit("ms_itemized_deductions_unit", period)
        prorate_fraction = person("ms_prorate_fraction", period)
        return deductions * prorate_fraction
