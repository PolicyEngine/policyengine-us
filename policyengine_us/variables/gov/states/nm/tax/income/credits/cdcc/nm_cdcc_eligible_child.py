from policyengine_us.model_api import *


class nm_cdcc_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for the New Mexico dependent child day care credit"
    definition_period = YEAR
    reference = "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503752/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgDsfAEwBKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA"
    defined_for = StateCode.NM

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nm.tax.income.credits.cdcc
        age = person("age", period)
        age_eligible = age < p.age_eligible
        dependent = person("is_tax_unit_dependent", period)
        # NMSA 7-2-18.1 counts a dependent as defined in IRC 152, and under
        # IRC 152(b)(1) a return on which the filer (or, if joint, either
        # spouse) can be claimed as a dependent has no dependents.
        dependent_filer = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
        )
        return age_eligible & dependent & ~dependent_filer
