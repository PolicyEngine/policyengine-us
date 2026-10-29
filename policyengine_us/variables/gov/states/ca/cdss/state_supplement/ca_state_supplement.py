from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)
from policyengine_us.variables.gov.states.ca.cdss.capi._ca_capi_ssi_ssp_standard import (
    ca_capi_ssi_ssp_standard,
)


class ca_state_supplement(Variable):
    value_type = float
    entity = SPMUnit
    label = "California state supplement"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200",
        "https://www.law.cornell.edu/cfr/text/20/416.1160",
        "https://www.cdss.ca.gov/Portals/9/CAPI/CAPI_Regulations-Accessible.pdf#page=25",
    )

    def formula(spm_unit, period, parameters):
        payment_standard = spm_unit("ca_state_supplement_payment_standard", period)
        ssi = add(spm_unit, period, ["ssi"])
        person = spm_unit.members
        # SSI/SSP counts another member's income only when it is deemed
        # (20 CFR 416.1160(a)), and CAPI budgets its own members' income (CAPI
        # regulations MPP 49-035), so the income of a member who fails SSI's
        # citizen or qualified-noncitizen test is not counted.
        immigration_status = person("immigration_status", period.this_year)
        is_citizen = immigration_status == immigration_status.possible_values.CITIZEN
        is_qualified_noncitizen = person(
            "is_ssi_qualified_noncitizen", period.this_year
        )
        meets_ssi_immigration_test = is_citizen | is_qualified_noncitizen
        # SSA treats a spouse who fails that test as an ineligible spouse (20
        # CFR 416.1160(d)). If the spouse receives CAPI, none of the income
        # counted for CAPI is deemed (20 CFR 416.1161(a)(2)-(3)), so the
        # recipient's own income counts, not half of the couple's. Otherwise
        # the spouse's income is deemed and SSA pays the lesser of the
        # individual and couple computations (20 CFR 416.1163).
        # NOTE: SSI couple status ignores SSI's noncitizen test, so the
        # model's SSI is still the couple computation (issue 10481).
        head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        spouse_fails_test = (
            person.marital_unit.sum(~meets_ssi_immigration_test & head_or_spouse) > 0
        )
        in_mixed_couple = (
            person("ssi_couple_computation_applies", period)
            & meets_ssi_immigration_test
            & spouse_fails_test
        )
        earned = max_(
            person("ssi_earned_income", period.this_year)
            - person(
                "ssi_blind_or_disabled_working_student_exclusion", period.this_year
            ),
            0,
        )
        # NOTE: in-kind support uses the couple's presumed maximum value here,
        # because SSI still treats the pair as a couple.
        unearned = person("ssi_unearned_income", period.this_year) + person(
            "ssi_in_kind_support_and_maintenance", period.this_year
        )
        # _apply_ssi_exclusions takes and returns annual amounts.
        own_countable_income = (
            _apply_ssi_exclusions(earned, unearned, parameters, period) / MONTHS_IN_YEAR
        )
        ssi_countable_income = person("ssi_countable_income", period)
        couple_income = person.marital_unit.sum(ssi_countable_income)
        individual_standard, couple_standard = ca_capi_ssi_ssp_standard(
            person, period, parameters
        )
        # The spouse receives CAPI when the couple standard exceeds the
        # couple's income plus the recipient's SSI/SSP on own income
        # (CAPI MPP 49-050.13, 49-035.221).
        recipient_ssi_ssp = max_(
            person("ssi", period), individual_standard - own_countable_income
        )
        spouse_gets_capi = couple_standard - couple_income - recipient_ssi_ssp > 0
        deemed_countable_income = max_(
            own_countable_income,
            couple_income - (couple_standard - individual_standard),
        )
        mixed_countable_income = where(
            spouse_gets_capi, own_countable_income, deemed_countable_income
        )
        person_countable_income = where(
            in_mixed_couple, mixed_countable_income, ssi_countable_income
        )
        countable_income = spm_unit.sum(
            where(meets_ssi_immigration_test, person_countable_income, 0)
        )
        return max_(0, payment_standard - ssi - countable_income)
