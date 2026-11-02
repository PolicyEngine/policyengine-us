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
        "https://www.dhhs.nh.gov/sr_htm/html/sr_26-01_dated_01_26.htm",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nh.dhhs.ssp
        arrangement = person("nh_ssp_living_arrangement", period)
        spouse = nh_ssp_spouse(person, period)
        size = person("nh_ssp_assistance_group_size", period)
        # He-W 658.03(e) and 648.04(b): the standard of need is the SSI maximum
        # for the group plus the minimum payment level less the standard
        # disregard, so it moves with each SSI cost-of-living increase.
        ssi = parameters(period).gov.ssa.ssi.amount
        disregard = p.standard_disregard[size]
        level = p.minimum_payment_level
        one_person = ssi.individual + level.one_person[arrangement] - disregard
        two_person = ssi.couple + level.two_person - disregard
        standard = select(
            [size == 3, size == 2],
            [p.three_person_need, two_person],
            default=one_person,
        )
        income = person("nh_ssp_countable_income", period)
        grant = np.floor(max_(standard - income, 0) + 0.5)
        # He-W 670.03(a)(4): no payment when the rounded grant is below the minimum.
        grant = where(grant >= p.minimum_payment, grant, 0)
        # He-W 670.03(c) reduces "the adult category grant pursuant to (a)", and
        # the rule does not apply the minimum again afterwards, so a reduced $2
        # grant pays $1. Either spouse's flag reduces the group grant.
        reduction = person("nh_ssp_grant_reduction_applies", period)
        reduction = reduction | spouse_value(reduction, spouse, False)
        grant = np.floor(grant * (1 - reduction * p.grant_reduction_fraction) + 0.5)
        # Applicant spouses split the couple's grant.
        eligible = person("nh_ssp_eligible", period)
        recipients = eligible.astype(int) + spouse_value(eligible, spouse, False)
        return grant / max_(recipients, 1)
