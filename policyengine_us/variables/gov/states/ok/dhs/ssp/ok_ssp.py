from policyengine_us.model_api import *


class ok_ssp(Variable):
    value_type = float
    entity = Person
    label = "Oklahoma State Supplemental Payment"
    definition_period = MONTH
    unit = USD
    reference = (
        "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-15-1-5",
        "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-15-1-4",
        "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-15-1-2",
        "https://www.oklahoma.gov/ohca/policies-and-rules/xpolicy/medical-assistance-for-adults-and-children-eligibility/eligibility-and-countable-income/countable-income-and-resources/determination-of-countable-income-for-individuals-categorically-.html",
    )
    defined_for = "ok_ssp_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ok.dhs.ssp
        ssi = parameters(period).gov.ssa.ssi.amount
        # OAC 340:15-1-4(9)(B)(i): countable income must be less than 100
        # percent of the FBR plus the maximum SSP amount.
        individual_standard = ssi.individual + p.maximum_payment
        couple_standard = ssi.couple + 2 * p.maximum_payment
        eligible = person("ok_ssp_eligible", period)
        joint = person.marital_unit.sum(eligible) == 2
        # NOTE: OAC 340:15-1-2 defines an ineligible spouse as one who is not
        # aged, blind or disabled, and is silent on an aged, blind or disabled
        # spouse who is not eligible. 340:15-1-4(10) applies 317:35-5-42, whose
        # (k)(1) defines an ineligible spouse as one living in the household
        # who "is not eligible for Supplemental Security Income (SSI)", as SSI
        # deeming does. Any spouse living together who is not SSP-eligible is
        # therefore treated as an ineligible spouse. Essential spouses (in the
        # case before 1974) are not modeled separately.
        arrangement = person("ssi_federal_living_arrangement", period)
        in_facility = person("ssi_lives_in_medical_treatment_facility", period) | (
            arrangement == arrangement.possible_values.MEDICAL_TREATMENT_FACILITY
        )
        apart = in_facility | person("is_incarcerated", period)
        ineligible_spouse = person.marital_unit.sum(~eligible & ~apart) > 0
        own = person("ok_ssp_own_countable_income", period)
        combined = person("ok_ssp_countable_income", period)
        standard = where(
            joint,
            couple_standard,
            where(ineligible_spouse, p.ineligible_spouse_standard, individual_standard),
        )
        income = where(joint | ineligible_spouse, combined, own)
        gap = max_(standard - income, 0)
        # OAC 340:15-1-5(c)(1)(B) and Appendix C-1 Schedule VIII.A give one
        # spouse the odd dollar without naming which, so person-level amounts
        # follow member order while the couple total does not.
        first_share = np.floor(gap / 2)
        first = person.marital_unit.reference_entity.members_position == 0
        payment = where(joint, where(first, first_share, gap - first_share), gap)
        # NOTE: 340:15-1-5(c)(6) tests a blind or disabled minor's income plus
        # deemed parental income against the SSP standard for an individual,
        # while 340:15-1-4(9)(B)(iii) and Appendix C-1 Schedule VIII.C say it
        # must be less than the FBR. The model follows the (c)(6) procedure.
        own_test = joint | (own < individual_standard)
        return own_test * min_(payment, p.maximum_payment)
