from policyengine_us.model_api import *


def sc_liheap_award(spm_unit, period, parameters, amounts, fuel_amount):
    """Return a seasonal nonemergency award from the supplied amount schedule.

    Heating and cooling share the household supplements and the mixed-status
    proration. Each season has its own amounts and maximum; only heating adds
    a fuel supplement, passed as fuel_amount.
    """
    p = parameters(period).gov.states.sc.oeo.liheap.payment
    income = spm_unit("sc_liheap_countable_income", period)
    size = spm_unit("sc_liheap_household_size", period)
    # The accepted plan's 30% governs over the older matrix's 70%. Both are shares
    # of the income limit: OEO's draft guide writes "30 of 60 percent of the SMI"
    # and "SMI is 60% of the State's Median Income".
    limit = spm_unit("sc_liheap_income_limit", period)
    low_income = income <= p.low_income_limit_rate * limit
    person = spm_unit.members
    age = person("age", period)
    # OEO's 2024 guide leaves state-placed foster children out of the household
    # and counts only eligible members for the itemized supplements.
    member = ~person("is_in_foster_care", period.first_month)
    eligible = member & person("is_citizen_or_legal_immigrant", period)
    elderly = spm_unit.any(eligible & (age >= p.ages.elderly_min))
    child = spm_unit.any(eligible & (np.floor(age) <= p.ages.child_max))
    disabled = spm_unit.any(eligible & person("is_disabled", period))
    veteran = spm_unit.any(eligible & person("is_veteran", period))
    # The plan measures home-energy utilities; aggregate existing heating and
    # electric bills, excluding water, sewer, trash, phone and separate cooking
    # fuel. Annual expenses approximate current monthly bills, and rent-embedded
    # charges are not available.
    cost = add(spm_unit, period, p.energy_cost_sources)
    high_burden = (cost > 0) & (cost >= income * p.burden_rate)
    a = amounts
    amount = (
        a.base
        + a.elderly * elderly
        + a.child * child
        + a.disabled * disabled
        + a.veteran * veteran
        + a.low_income * low_income
        + a.high_burden * high_burden
        + fuel_amount
    )
    # Local funding and priority decisions are not represented. The state
    # schedule does not impose a general benefit-to-bill cap.
    # The plans state each season's maximum; that season's amounts sum to
    # exactly it.
    award = min_(amount, a.maximum)
    # A mixed-status award is the total benefit / all household members x
    # eligible members; both counts leave out state-placed foster children.
    # An eligible unit always has a member, so the floor only avoids dividing by zero.
    return award * size / max_(spm_unit.sum(member), 1)


class sc_liheap(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina LIHEAP regular heating assistance"
    unit = USD
    definition_period = YEAR
    defined_for = "sc_liheap_eligible"
    reference = (
        # PDF pages 8-9
        "https://oeo.sc.gov/managedsites/prd/oeo/documents/2026%20LIHEAP%20State%20Plan.pdf#page=8",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/SC_BenefitMatrix_2026.pdf#page=2",
        # PDF pages 311-312,338,529,537,546
        "https://oeo.sc.gov/managedsites/prd/oeo/documents/2026%20South%20Carolina%20LIHEAP%20Model%20Plan%20w%20Attachments.pdf#page=311",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sc.oeo.liheap.payment
        fuel = spm_unit("heating_type", period)
        fuel_supplement = np.isin(fuel.decode_to_str(), p.supplement_fuels)
        return sc_liheap_award(
            spm_unit, period, parameters, p.amounts, p.amounts.fuel * fuel_supplement
        )
