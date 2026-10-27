from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ca.cdss.capi._ca_capi_ssi_ssp_standard import (
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
        countable_income = person("ssi_countable_income", period)
        payment_standard = person("ca_capi_payment_standard", period)
        deemed_income = person("ssi_income_deemed_from_ineligible_spouse", period)
        own_income = max_(countable_income - deemed_income, 0)
        # Deeming needs an ineligible spouse living in the same household
        # (20 CFR 416.1160(a)(1)), so a Title XIX facility resident counts
        # only their own income.
        medical_facility = person("ca_in_medical_care_facility", period.this_year)
        income = where(medical_facility, own_income, countable_income)
        # NOTE: the reduced-needs standards for another person's household are
        # not modeled (issue 7892), so those recipients get the
        # independent-living standard.
        benefit = max_(payment_standard - income, 0)

        # Mixed couple: the spouse's SSI/SSP counts as unearned income based on
        # need (MPP 49-035.221), subtracted with the couple's countable income
        # from the couple standard (MPP 49-055.32).
        # NOTE: the model applies this computation whenever both spouses are
        # aged, blind or disabled (ssi_couple_computation_applies ignores SSI's
        # noncitizen test), even when SSA would pay the spouse nothing. Such a
        # spouse is an ineligible spouse (MPP 49-005(i)(2); 20 CFR 416.1160(d))
        # and deeming applies. Example, January 2026: a citizen with $1,300 of
        # Social Security and a CAPI spouse with no income get $818.83 a month
        # in the model; the law gives $450.94 of CAPI alone (issue 10481).
        capi_eligible = person("ca_capi_eligible_person", period.this_year)
        joint = person("ssi_couple_computation_applies", period)
        mixed = joint & ~(person.marital_unit.sum(capi_eligible) > 1)
        spouse = ~capi_eligible
        spouse_ssi = person.marital_unit.sum(person("ssi", period) * spouse)
        # NOTE: ca_state_supplement is an SPM-unit amount; as a simplification,
        # the spouse's share is pro rata among the unit's SSP-eligible members.
        ssp_eligible = person("ca_state_supplement_eligible_person", period)
        spouse_ssp_share = person.marital_unit.sum(ssp_eligible * spouse) / max_(
            person.spm_unit.sum(ssp_eligible), 1
        )
        spouse_ssp = spouse_ssp_share * person.spm_unit("ca_state_supplement", period)
        couple_income = person.marital_unit.sum(countable_income)
        mixed_benefit = max_(
            payment_standard - couple_income - spouse_ssi - spouse_ssp, 0
        )

        # MPP 49-035.71 follows the SSI spouse-to-spouse deeming steps: compute
        # the federal and state parts as an individual and under deeming, then
        # take the lesser of each (POMS SI 01320.430 D). WIC 18940(b) applies
        # the federal deeming rules and WIC 18941 makes CAPI equal SSI/SSP,
        # which SSA computes this way; the 1999 CAPI form SOC 452 takes the
        # lesser of the two totals instead.
        # NOTE: the federal parts use the independent-living benefit rates,
        # matching the independent-living SSI/SSP standards.
        individual_standard, couple_standard = ca_capi_ssi_ssp_standard(
            person, period, parameters
        )
        fbr = parameters(period).gov.ssa.ssi.amount
        individual_federal = fbr.individual - own_income
        couple_federal = fbr.couple - countable_income
        federal = max_(min_(individual_federal, couple_federal), 0)
        individual_supplement = individual_standard - fbr.individual
        couple_supplement = max_(couple_standard - fbr.couple, individual_supplement)
        # Income above a federal rate reduces the matching state supplement.
        supplement = min_(
            individual_supplement + min_(individual_federal, 0),
            couple_supplement + min_(couple_federal, 0),
        )
        p = parameters(period).gov.states.ca.cdss.capi.payment_standard_offset
        deemed_benefit = max_(federal + supplement - p.single, 0)
        deeming = (
            person("is_ssi_spousal_deeming_applies", period.this_year)
            & ~joint
            & ~medical_facility
        )
        return select(
            [mixed, deeming],
            [mixed_benefit, deemed_benefit],
            default=benefit,
        )
