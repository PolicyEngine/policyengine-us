from policyengine_us.model_api import *


class medicaid_parent_income_limit(Variable):
    value_type = float
    entity = Person
    label = "Medicaid parent income limit"
    unit = "/1"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.110",
        "https://www.dmas.virginia.gov/media/0aynyhxk/m04-1-1-26a.pdf#page=51",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.categories.parent
        va_lifc = parameters(period).gov.states.va.dmas.medicaid.lifc
        fl_parent = parameters(period).gov.states.fl.dcf.medicaid.parent
        state = person.household("state_code_str", period)
        state_code = person.household("state_code", period)
        national_limit = p.income_limit[state]
        if va_lifc.in_effect:
            national_limit = where(
                state_code == StateCode.VA,
                person("va_medicaid_lifc_income_limit", period),
                national_limit,
            )
        if fl_parent.in_effect:
            national_limit = where(
                state_code == StateCode.FL,
                person("fl_medicaid_parent_income_limit", period),
                national_limit,
            )
        tx_parent = parameters(period).gov.states.tx.hhs.medicaid.parent
        if tx_parent.in_effect:
            # This bounded route verifies the one-parent column only where an
            # identified adult parent is the household's sole adult and sole
            # identified parent. Multiple-adult, two-parent and unidentified
            # households keep their existing ratio; their classification is
            # not inferred from tax filing or the parent NFC proxy.
            age = person("age", period)
            is_parent = person("is_parent", period)
            minimum_adult_age = tx_parent.verified_subset_minimum_adult_age
            only_adult = person.household.sum(age >= minimum_adult_age) == 1
            only_parent = person.household.sum(is_parent) == 1
            tx_one_parent = (
                (state_code == StateCode.TX)
                & (age >= minimum_adult_age)
                & is_parent
                & only_adult
                & only_parent
            )
            national_limit = where(
                tx_one_parent,
                person("tx_medicaid_parent_income_limit", period),
                national_limit,
            )
        return where(
            state_code == StateCode.MO,
            person("mo_mhf_parent_income_limit", period),
            national_limit,
        )
