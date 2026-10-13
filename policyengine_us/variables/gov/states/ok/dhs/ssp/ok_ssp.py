from policyengine_us.model_api import *


class ok_ssp(Variable):
    value_type = float
    entity = Person
    label = "Oklahoma State Supplemental Payment"
    definition_period = MONTH
    unit = USD
    reference = "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-15-1-5"
    defined_for = "ok_ssp_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ok.dhs.ssp
        ssi = parameters(period).gov.ssa.ssi.amount
        individual_standard = ssi.individual + p.maximum_payment
        couple_standard = ssi.couple + 2 * p.maximum_payment
        recipients = person.marital_unit.sum(person("ok_ssp_eligible", period))
        joint = recipients == 2
        # OAC 340:15-1-2: an ineligible spouse lives with the individual and is
        # not aged, blind or disabled. With any other spouse the claimant is an
        # individual. Essential spouses (in the case before 1974) are not
        # modeled separately.
        abd = person("is_ssi_aged_blind_disabled", period.this_year)
        arrangement = person("ssi_federal_living_arrangement", period)
        in_facility = person("ssi_lives_in_medical_treatment_facility", period) | (
            arrangement == arrangement.possible_values.MEDICAL_TREATMENT_FACILITY
        )
        apart = in_facility | person("is_incarcerated", period)
        ineligible_spouse = person.marital_unit.sum(~abd & ~apart) > 0
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
        own_test = joint | (own < individual_standard)
        return own_test * min_(payment, p.maximum_payment)
