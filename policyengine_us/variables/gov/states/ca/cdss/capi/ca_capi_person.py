from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_total,
)
from policyengine_us.variables.gov.states.ca.cdss.capi._ca_capi_ssi_ssp_standard import (
    ca_capi_couple_computation,
    ca_capi_in_title_xix_facility,
    ca_capi_spouse_ssi_ssp,
    ca_capi_ssi_ssp_standard,
)


class ca_capi_person(Variable):
    value_type = float
    entity = Person
    label = "California CAPI amount per person"
    unit = USD
    definition_period = MONTH
    defined_for = "ca_capi_eligible_person"
    reference = (
        # PDF pages 3-4,25,30,47
        "https://www.cdss.ca.gov/Portals/9/CAPI/CAPI_Regulations-Accessible.pdf#page=3",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=18940",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=18941",
        "https://secure.ssa.gov/poms.nsf/lnx/0501320430",
        "https://www.law.cornell.edu/cfr/text/20/416.1160",
    )

    def formula(person, period, parameters):
        # When only the California facility input separates a couple that SSI
        # computes jointly, ssi_countable_income holds half the couple's
        # income; each spouse's own income counts (20 CFR 416.414(b)(3)).
        # NOTE: this own income leaves out in-kind support and the student
        # earned income exclusion, which SSI's joint computation would apply.
        separated = person(
            "ssi_couple_computation_applies", period
        ) & ~ca_capi_couple_computation(person, period)
        own_alone = (
            _apply_ssi_exclusions(
                person("ssi_earned_income", period.this_year),
                person("ssi_unearned_income", period.this_year),
                parameters,
                period.this_year,
            )
            / MONTHS_IN_YEAR
        )
        countable_income = where(
            separated, own_alone, person("ssi_countable_income", period)
        )
        payment_standard = person("ca_capi_payment_standard", period)
        deemed_income = person("ssi_income_deemed_from_ineligible_spouse", period)
        own_income = max_(countable_income - deemed_income, 0)
        # Deeming needs an ineligible spouse living in the same household
        # (20 CFR 416.1160(a)(1)), so a Title XIX facility resident counts
        # only their own income.
        medical_facility = ca_capi_in_title_xix_facility(person, period)
        income = where(medical_facility, own_income, countable_income)
        # NOTE: the reduced-needs standards for another person's household are
        # not modeled (issue 7892), so those recipients get the
        # independent-living standard.
        benefit = max_(payment_standard - income, 0)

        # Mixed couple: the spouse's SSI/SSP counts as unearned income based on
        # need (MPP 49-035.221), subtracted with the couple's countable income
        # from the couple standard (MPP 49-055.32).
        # NOTE: SSI couple status ignores SSI's noncitizen test, so the model
        # can still pay such a spouse SSI that SSA would not (issue 10481).
        capi_eligible = person("ca_capi_eligible_person", period.this_year)
        joint = ca_capi_couple_computation(person, period)
        couple_with_spouse = joint & ~(
            _ssi_couple_total(person, period.this_year, capi_eligible.astype(int)) > 1
        )
        spouse_ssi_ssp = ca_capi_spouse_ssi_ssp(person, period)
        couple_income = _ssi_couple_total(person, period.this_year, countable_income)
        # A spouse counts as an eligible spouse only while receiving SSI/SSP
        # (MPP 49-005(e)(3), 49-050.13). A spouse paid neither is an
        # ineligible spouse (MPP 49-005(i)(2)), whose income is deemed.
        spouse_paid = spouse_ssi_ssp > 0
        mixed = couple_with_spouse & spouse_paid
        unpaid_spouse = couple_with_spouse & ~spouse_paid
        mixed_benefit = max_(payment_standard - couple_income - spouse_ssi_ssp, 0)

        # MPP 49-035.71 follows the SSI spouse-to-spouse deeming steps: the
        # federal and state parts are each the lesser of the individual and the
        # deeming computation (POMS SI 01320.430 D; WIC 18940(b), 18941). The
        # 1999 CAPI form SOC 452 takes the lesser of the two totals instead.
        # NOTE: the federal parts use the independent-living benefit rates.
        individual_standard, couple_standard = ca_capi_ssi_ssp_standard(
            person, period, parameters
        )
        fbr = parameters(period).gov.ssa.ssi.amount
        individual_federal = fbr.individual - own_income
        deeming_income = where(unpaid_spouse, couple_income, countable_income)
        couple_federal = fbr.couple - deeming_income
        federal = max_(min_(individual_federal, couple_federal), 0)
        individual_supplement = individual_standard - fbr.individual
        # NOTE: a guard (POMS SI 01320.430 C.4.c); the couple state part exceeds
        # the individual part in every modeled year.
        couple_supplement = max_(couple_standard - fbr.couple, individual_supplement)
        # Income above a federal rate reduces the matching state supplement.
        supplement = min_(
            individual_supplement + min_(individual_federal, 0),
            couple_supplement + min_(couple_federal, 0),
        )
        p = parameters(period).gov.states.ca.cdss.capi.payment_standard_offset
        deemed_benefit = max_(federal + supplement - p.single, 0)
        # NOTE: until PR 10240 counts the income of people who fail SSI's
        # noncitizen test, deeming from a spouse who is not aged, blind or
        # disabled runs only with supplied inputs.
        deeming = (
            (person("is_ssi_spousal_deeming_applies", period.this_year) & ~joint)
            | unpaid_spouse
        ) & ~medical_facility
        return select(
            [mixed, deeming],
            [mixed_benefit, deemed_benefit],
            default=benefit,
        )
