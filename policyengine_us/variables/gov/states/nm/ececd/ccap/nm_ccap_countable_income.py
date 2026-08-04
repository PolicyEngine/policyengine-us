from policyengine_us.model_api import *


class nm_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Mexico CCAP countable income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.NM
    reference = "https://www.srca.nm.gov/parts/title08/08.015.0002.html"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nm.ececd.ccap.income.countable_income
        # 8.15.2.11.C(3): household income excludes the earned and unearned
        # income of legal dependents and of grandparents who are not legal
        # guardians. Count only caretakers (tax unit head/spouse), so household
        # children's income is excluded. SSDI is omitted from the sources list,
        # so it is exempt for everyone (8.15.2.11.C(6)).
        person = spm_unit.members
        is_caretaker = person("is_tax_unit_head_or_spouse", period.this_year)
        person_income = add(person, period, p.sources)
        return spm_unit.sum(person_income * is_caretaker)
