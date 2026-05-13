from policyengine_us.model_api import *


class ms_standard_deduction_joint(Variable):
    value_type = float
    entity = Person
    label = "Mississippi personal standard deduction for married couples filing jointly"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS
    reference = (
        "https://law.justia.com/codes/mississippi/title-27/chapter-7/article-1/section-27-7-17/",  # MS Code 27-7-17: deductions may be divided in any manner
    )

    def formula(person, period, parameters):
        filing_status = person.tax_unit("filing_status", period)
        p = parameters(period).gov.states.ms.tax.income.deductions.standard

        prorate_fraction = person("ms_prorate_fraction", period)
        return p.amount[filing_status] * prorate_fraction
