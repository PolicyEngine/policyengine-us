from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)
from policyengine_us.variables.gov.ssa.ssi._ssi_living_arrangement_amount import (
    ssi_living_arrangement_amount,
)


class uncapped_ssi_without_spousal_deeming(Variable):
    value_type = float
    entity = Person
    label = "Uncapped SSI without spousal deeming"
    unit = USD
    documentation = (
        "Individual federal benefit rate less only the person's own countable "
        "income, the amount SSI under spousal deeming cannot exceed (can be "
        "below zero)."
    )
    definition_period = MONTH
    defined_for = "is_ssi_eligible"
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1163#p-416.1163(e)(2)",
        "https://secure.ssa.gov/poms.nsf/lnx/0501320150",
        "https://secure.ssa.gov/poms.nsf/lnx/0501320400",
        "https://secure.ssa.gov/poms.nsf/lnx/0500835300",
    )

    def formula(person, period, parameters):
        # 416.1163(e)(2): 'the amount remaining after we subtract only your
        # own countable income from an individual's Federal benefit rate'.
        # The rate takes the same living-arrangement adjustments as the rate
        # under deeming.
        # NOTE: We do not model 416.1163(f)(5) (issue 10455).
        p = parameters(period).gov.ssa.ssi
        amount = ssi_living_arrangement_amount(
            person, period, parameters, p.amount.individual
        )
        # Countable income adds income deemed from an ineligible spouse to the
        # person's own countable income; remove it.
        own_countable_income = person("ssi_countable_income", period) - person(
            "ssi_income_deemed_from_ineligible_spouse", period
        )
        # SSA applies the regular individual PMV to this individual
        # computation (POMS SI 01320.150 B.1.b and SI 01320.400 C.2).
        # Reapply the exclusions because a rebutted ISM amount can leave
        # part of the general exclusion available for earned income.
        year = period.this_year
        pmv_applies = person("ssi_pmv_applies", year)
        deeming_applies = person("is_ssi_spousal_deeming_applies", year)
        individual_pmv = (
            p.amount.individual * p.income.ism.pmv_fbr_fraction
            + p.income.exclusions.general
        ) * MONTHS_IN_YEAR
        actual_ism = person("ssi_shelter_support_value", year)
        individual_ism = where(
            actual_ism > 0, min_(individual_pmv, actual_ism), individual_pmv
        )
        earned = max_(
            person("ssi_earned_income", year)
            - person("ssi_blind_or_disabled_working_student_exclusion", year),
            0,
        )
        unearned = (
            person("ssi_unearned_income", year)
            + person("ssi_unearned_income_deemed_from_ineligible_parent", year)
            + individual_ism
        )
        individual_countable = (
            _apply_ssi_exclusions(earned, unearned, parameters, year) / MONTHS_IN_YEAR
        )
        own_countable_income = where(
            pmv_applies & deeming_applies,
            individual_countable,
            own_countable_income,
        )
        return amount - own_countable_income
