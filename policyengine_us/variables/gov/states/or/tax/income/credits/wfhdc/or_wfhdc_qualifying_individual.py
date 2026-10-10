from policyengine_us.model_api import *


class or_wfhdc_qualifying_individual(Variable):
    value_type = bool
    entity = Person
    label = "Qualifying individual for the Oregon Working Family Household and Dependent Care Credit"
    definition_period = YEAR
    reference = (
        "https://www.oregon.gov/dor/forms/FormsPubs/schedule-or-wfhdc-inst_101-195-1_2025.pdf#page=2",
        "https://law.justia.com/codes/oregon/2021/volume-08/chapter-315/section-315-264/",
        "https://www.law.cornell.edu/uscode/text/26/21#b_1",
    )
    defined_for = StateCode.OR

    def formula(person, period, parameters):
        p = parameters(period).gov.states["or"].tax.income.credits.wfhdc
        # ORS 315.264 takes the qualifying individuals of IRC 21(b)(1): a
        # child dependent (a return on which a filer can be claimed has no
        # dependents, IRC 152(b)(1)); a disabled dependent, determined without
        # regard to 152(b)(1); and a disabled spouse. Schedule OR-WFHDC:
        # "the word 'you' also refers to your spouse", so on a joint return
        # either spouse can be the other's qualifying individual.
        age = person("age", period)
        disabled = person("is_disabled", period)
        dependent = person("is_tax_unit_dependent", period)
        filer = person("is_tax_unit_head_or_spouse", period)
        married = person.tax_unit("tax_unit_married", period)
        dependent_filer = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere", period
        )
        child = dependent & (age <= p.child_age_limit) & ~dependent_filer
        disabled_dependent = dependent & disabled
        disabled_spouse = filer & disabled & married
        return child | disabled_dependent | disabled_spouse
