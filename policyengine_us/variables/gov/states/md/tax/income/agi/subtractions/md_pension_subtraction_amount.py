from policyengine_us.model_api import *


class md_pension_subtraction_amount(Variable):
    value_type = float
    entity = Person
    label = "MD pension subtraction from AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-2-maryland-taxable-income-calculations-for-individual/part-ii-maryland-adjusted-gross-income/section-10-208-effective-until-712024-subtractions-from-federal-adjusted-gross-income-state-adjustments"
        "https://www.marylandtaxes.gov/forms/21_forms/Resident_Booklet.pdf#page=13"
    )
    defined_for = StateCode.MD

    def formula(person, period, parameters):
        p = parameters(period).gov.states.md.tax.income.agi.subtractions
        # determine pension subtraction eligiblity for each person
        dependent = person("is_tax_unit_dependent", period)
        min_age = p.pension_subtraction_min_age
        elderly = person("age", period) >= min_age
        disabled = person("is_permanently_and_totally_disabled", period)
        partner_is_disabled = False  # TODO: construct demographic variable
        eligible = ~dependent & (elderly | disabled | partner_is_disabled)
        # calculate pension subtraction amount for each person
        peninc = person("taxable_pension_income", period)
        socsec = person("social_security", period)
        max_amount = p.pension_subtraction_max
        amount = min_(peninc, max_(0, max_amount - socsec))
        # return pension subtraction amount for each eligible person
        return eligible * amount
