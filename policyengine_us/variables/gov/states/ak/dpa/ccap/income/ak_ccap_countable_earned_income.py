from policyengine_us.model_api import *


class ak_ccap_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alaska CCAP countable earned income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.AK
    reference = (
        "https://www.akleg.gov/statutesPDF/aac%20Title%207.pdf#page=907",
        "https://health.alaska.gov/media/igiccwuf/child-care-assistance-program-policies-and-procedures.pdf#page=203",
    )

    def formula(spm_unit, period, parameters):
        # Manual §4080-2 J.4 prorates annual self-employment income over
        # 12 months when self-employment income exceeds 185% of the federal
        # poverty guideline for the family size, and over the "months of
        # normal season of work" otherwise. We don't model the seasonal
        # branch at the moment because PolicyEngine treats
        # `self_employment_income` as annualized; the standard period
        # conversion from annual to monthly approximates the >185% FPG
        # branch.
        p_income = parameters(period).gov.states.ak.dpa.ccap.income.countable_income
        adult_age = parameters(period).gov.states.ak.dpa.ccap.age_threshold.adult
        person = spm_unit.members
        is_adult = person("age", period.this_year) >= adult_age
        earned_per_person = sum(
            person(source, period) for source in p_income.earned_sources
        )
        return spm_unit.sum(earned_per_person * is_adult)
