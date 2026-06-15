from policyengine_us.model_api import *


class la_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "Louisiana CCAP countable income"
    unit = USD
    reference = "https://www.doa.la.gov/media/043btqeh/28v165.docx"
    defined_for = StateCode.LA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.la.ldoe.ccap.income
        person = spm_unit.members
        # LAC 28:CLXV.509.A.3.a counts gross earnings of the head of household
        # and the legal or non-legal spouse; minor unmarried parents are not
        # tracked separately at the moment.
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        # §509.A.3.a counts gross earnings: a net loss from self-employment
        # or farm operations yields zero gross earnings and cannot offset
        # other earned income, so each source is floored at zero.
        earned = sum(max_(person(source, period), 0) for source in p.earned_sources)
        countable_earned = spm_unit.sum(earned * is_head_or_spouse)
        # LAC 28:CLXV.509.A.3.b counts enumerated recurring unearned income of
        # all household members.
        unearned = add(spm_unit, period, p.unearned_sources)
        return countable_earned + unearned
