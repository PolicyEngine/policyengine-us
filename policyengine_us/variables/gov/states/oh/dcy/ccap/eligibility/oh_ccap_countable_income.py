from policyengine_us.model_api import *


class oh_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Ohio CCAP countable income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.OH
    reference = "https://codes.ohio.gov/ohio-administrative-code/rule-5180:2-16-03"

    def formula(spm_unit, period, parameters):
        # 5180:2-16-03: countable income is gross earned plus gross unearned
        # income, minus the enumerated exclusions. The countable sources are
        # listed in income/countable_income/sources.yaml.
        p = parameters(period).gov.states.oh.dcy.ccap.income
        sources = add(spm_unit, period, p.countable_income.sources)
        # 5180:2-16-03(F)(8) & (I)(1): SSI is excluded, and so is any income
        # earned by a person receiving SSI. SSI itself is already omitted from
        # the sources list, but the earned-income exclusion cannot be expressed
        # by a list omission, so we subtract the earned income of SSI
        # recipients here.
        person = spm_unit.members
        receives_ssi = person("ssi", period) > 0
        person_earned_income = add(person, period, p.countable_income.earned_sources)
        ssi_recipient_earned_income = spm_unit.sum(person_earned_income * receives_ssi)
        return sources - ssi_recipient_earned_income
