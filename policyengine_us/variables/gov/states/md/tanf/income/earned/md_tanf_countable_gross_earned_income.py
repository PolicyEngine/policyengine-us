from policyengine_us.model_api import *


class md_tanf_countable_gross_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TCA countable gross earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MD
    reference = "https://dsd.maryland.gov/regulations/Pages/07.03.03.13.aspx"

    def formula(spm_unit, period, parameters):
        # Per COMAR 07.03.03.13, exclude:
        # 1. Earned income of a child
        # 2. Earned income of an SSI recipient
        person = spm_unit.members
        is_child = person("md_tanf_is_child", period)
        is_ssi_recipient = person("is_ssi_eligible", period.this_year)
        # Count only earned income from non-children and non-SSI recipients
        include_income = ~is_child & ~is_ssi_recipient
        # Get earned income sources from parameters
        earned_sources = parameters(
            period
        ).gov.states.md.tanf.income.sources.earned
        total_earned = add(person, period, earned_sources)
        countable_earned = total_earned * include_income
        return spm_unit.sum(countable_earned)
