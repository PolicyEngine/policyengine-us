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
        has_spouse = person.marital_unit.nb_persons() == 2
        spouse_tanf = (
            person.marital_unit.sum(person("ok_ssp_is_in_tanf_unit", period)) > 0
        )
        with_spouse = has_spouse & ~spouse_tanf
        own = person("ok_ssp_own_countable_income", period)
        combined = person("ok_ssp_countable_income", period)
        standard = where(
            joint,
            couple_standard,
            where(with_spouse, p.ineligible_spouse_standard, individual_standard),
        )
        income = where(with_spouse, combined, own)
        gap = max_(standard - income, 0)
        # Assign an indivisible dollar to the second member of the couple.
        first_share = np.floor(gap / 2)
        first = person.marital_unit.reference_entity.members_position == 0
        payment = where(joint, where(first, first_share, gap - first_share), gap)
        own_test = (
            joint
            | person("ok_ssp_has_essential_spouse", period)
            | (own < individual_standard)
        )
        return own_test * min_(payment, p.maximum_payment)
