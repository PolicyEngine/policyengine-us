from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.nh.dhhs.ssp._nh_ssp_couple import (
    nh_ssp_spouse,
    spouse_value,
)


class nh_ssp(Variable):
    value_type = float
    entity = Person
    label = "New Hampshire State Supplement Program"
    definition_period = MONTH
    unit = USD
    defined_for = "nh_ssp_eligible"
    reference = (
        # PDF pages 14-16
        "https://www.medicaid.gov/medicaid/spa/downloads/NH-26-0001.pdf#page=14",
        "https://gc.nh.gov/rules/state_agencies/he-w600.html",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nh.dhhs.ssp
        arrangement = person("nh_ssp_living_arrangement", period)
        independent = arrangement == arrangement.possible_values.INDEPENDENT
        spouse = nh_ssp_spouse(person, period)
        couple = spouse >= 0
        has_essential_person = person("nh_ssp_has_essential_person", period)
        essential = independent & (
            has_essential_person | spouse_value(has_essential_person, spouse, False)
        )
        standard = where(couple, p.couple_need, p.individual_need[arrangement])
        standard = where(
            essential, where(couple, p.three_person_need, p.couple_need), standard
        )
        income = person("nh_ssp_countable_income", period)
        grant = np.floor(max_(standard - income, 0) + 0.5)
        # He-W 670.03(a)(4): no payment when the rounded grant is below the minimum.
        grant = where(grant >= p.minimum_payment, grant, 0)
        # He-W 670.03(c) reduces the group grant, so either spouse's flag applies.
        reduction = person("nh_ssp_grant_reduction_applies", period)
        reduction = reduction | spouse_value(reduction, spouse, False)
        grant = np.floor(grant * (1 - reduction * p.grant_reduction_fraction) + 0.5)
        # Applicant spouses split the couple's grant.
        eligible = person("nh_ssp_eligible", period)
        recipients = eligible.astype(int) + spouse_value(eligible, spouse, False)
        return grant / max_(recipients, 1)
