from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi._ssi_state_supplement import (
    federal_supplement_payment,
    ssi_state_supplement,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_total,
)
from policyengine_us.variables.gov.states.ca.cdss.capi._ca_capi_ssi_ssp_standard import (
    ca_capi_couple_computation,
    ca_capi_ssi_ssp_standard,
)
from policyengine_us.variables.gov.states.ca.cdss.state_supplement._ca_state_supplement_rates import (
    ca_state_supplement_rates,
)


class ca_state_supplement_person(Variable):
    value_type = float
    entity = Person
    label = "California state supplement per person"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12150",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200",
        "https://secure.ssa.gov/apps10/poms.nsf/lnx/0501415058",
        "https://www.law.cornell.edu/cfr/text/20/416.1160",
        "https://www.law.cornell.edu/cfr/text/20/416.1161",
        "https://www.law.cornell.edu/cfr/text/20/416.2025",
        "https://www.cdss.ca.gov/Portals/9/CAPI/CAPI_Regulations-Accessible.pdf#page=25",
    )

    def formula(person, period, parameters):
        # A couple with one spouse in a Title XIX facility is computed
        # separately, including when only the California input marks it (20 CFR
        # 416.414(b)(3)).
        joint = ca_capi_couple_computation(person, period)
        individual_rate, couple_rate = ca_state_supplement_rates(
            person, period, parameters, joint
        )
        # SSA administers the supplement, so the federal income, couple,
        # deeming and rounding rules apply (POMS SI 01415.058 A).
        payment = ssi_state_supplement(
            person, period, parameters, individual_rate, couple_rate, joint=joint
        )

        # SSA treats a spouse who fails SSI's citizen or qualified-noncitizen
        # test as an ineligible spouse (20 CFR 416.1160(d)), but SSI couple
        # status ignores that test (issue 10481). So the model's SSI is the
        # couple computation, and the supplement makes up the rest of the
        # recipient's individual standard. If the spouse receives CAPI, none of
        # the income counted for CAPI is deemed (20 CFR 416.1161(a)(2)-(3)), so
        # the recipient's own income counts, not half of the couple's. Otherwise
        # the spouse's income is deemed (20 CFR 416.1163, 416.2025(b)(3)).
        # Taking the lesser of the individual and couple totals gives both:
        # it equals own income whenever the spouse would receive CAPI.
        # NOTE: POMS SI 01320.430 D takes the lesser of each part separately;
        # the totals keep CAPI at zero when the spouse's income is deemed.
        immigration_status = person("immigration_status", period.this_year)
        is_citizen = immigration_status == immigration_status.possible_values.CITIZEN
        is_qualified_noncitizen = person(
            "is_ssi_qualified_noncitizen", period.this_year
        )
        fails_test = ~(is_citizen | is_qualified_noncitizen)
        # The exclusion needs a spouse who can receive CAPI, so key on CAPI
        # eligibility rather than on SSI's noncitizen test alone (issue 10482).
        # Find the spouse as SSI's couple tests do, so the default marital
        # unit of a situation that omits marital units does not pair a
        # recipient with an unrelated member's CAPI eligibility or income.
        capi_eligible = person("ca_capi_eligible_person", period.this_year)
        spouse_capi_eligible = joint & (
            _ssi_couple_total(person, period.this_year, capi_eligible.astype(int)) > 0
        )
        split_couple = spouse_capi_eligible | (
            joint
            & (_ssi_couple_total(person, period.this_year, fails_test.astype(int)) > 0)
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
        couple_income = _ssi_couple_total(
            person, period.this_year, ssi_countable_income
        )
        individual_standard, couple_standard = ca_capi_ssi_ssp_standard(
            person, period, parameters
        )
        mixed_countable_income = max_(
            own_countable_income,
            couple_income - (couple_standard - individual_standard),
        )
        countable_income = where(
            spouse_capi_eligible, mixed_countable_income, ssi_countable_income
        )
        split_amount = max_(
            individual_standard - person("ssi", period) - countable_income, 0
        )
        split_payment = federal_supplement_payment(
            split_amount, parameters, period
        ) * person("takes_up_ssi_if_eligible", period.this_year)
        # WIC 12150 entitles people who receive SSI or "who but for their
        # income" could, which is SSI eligibility without its income test.
        eligible = person("is_ssi_eligible", period)
        return eligible * where(split_couple, split_payment, payment)
