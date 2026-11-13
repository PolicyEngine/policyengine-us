from policyengine_us.model_api import *


class oh_business_income_person(Variable):
    value_type = float
    entity = Person
    label = "Ohio business income for each filer"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",
        # 2024 Ohio IT 1040 instructions, Ohio Schedule of Business Income
        "https://dam.assets.ohio.gov/image/upload/tax.ohio.gov/forms/ohio_individual/individual/2024/it1040-booklet.pdf#page=26",
    )
    defined_for = StateCode.OH

    def formula(person, period, parameters):
        p = parameters(period).gov.states.oh.tax.income.business_income
        # The schedule lists the business income "that you (and your spouse,
        # if filing jointly) received"; a dependent's income is on the
        # dependent's own return. Losses net against gains.
        not_dependent = ~person("is_tax_unit_dependent", period)
        return not_dependent * add(person, period, p.sources)
