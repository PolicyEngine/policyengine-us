from policyengine_us.model_api import *


class nh_ssp(Variable):
    value_type = float
    entity = Person
    label = "New Hampshire State Supplement Program"
    definition_period = MONTH
    unit = USD
    defined_for = "nh_ssp_eligible"
    reference = (
        "https://www.medicaid.gov/medicaid/spa/downloads/NH-26-0001.pdf",
        "https://gc.nh.gov/rules/state_agencies/he-w600.html",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nh.dhhs.ssp
        arrangement = person("nh_ssp_living_arrangement", period)
        independent = arrangement == arrangement.possible_values.INDEPENDENT
        couple = independent & (person.marital_unit.sum(independent) == 2)
        essential = independent & person.marital_unit.any(
            person("nh_ssp_has_essential_person", period)
        )
        standard = where(couple, p.couple_need, p.individual_need[arrangement])
        standard = where(
            essential, where(couple, p.three_person_need, p.couple_need), standard
        )
        income = person("nh_ssp_countable_income", period)
        grant = np.floor(max_(standard - income, 0) + 0.5)
        grant = where(grant > 0, max_(grant, p.minimum_payment), 0)
        reduction = person("nh_ssp_grant_reduction_applies", period)
        grant = np.floor(grant * (1 - reduction * p.grant_reduction_fraction) + 0.5)
        recipients = person.marital_unit.sum(person("nh_ssp_eligible", period))
        return grant / where(couple, max_(recipients, 1), 1)
