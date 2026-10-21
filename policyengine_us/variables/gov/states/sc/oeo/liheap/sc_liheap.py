from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class sc_liheap(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina LIHEAP regular heating assistance"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC
    reference = (
        # PDF pages 8-9
        "https://oeo.sc.gov/managedsites/prd/oeo/documents/2026%20LIHEAP%20State%20Plan.pdf#page=8",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/SC_BenefitMatrix_2026.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sc.oeo.liheap.payment
        income = spm_unit("sc_liheap_countable_income", period)
        size = spm_unit("sc_liheap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        # The accepted plan's 30% SMI threshold governs over the older-vintage
        # matrix's conflicting 42% threshold. Keep the percentage boundary exact.
        low_income = income.astype(np.float64) <= p.low_income_smi_rate * smi(
            size, state, period, parameters
        )
        person = spm_unit.members
        age = person("age", period)
        elderly = spm_unit.any(age >= p.ages.elderly_min)
        child = spm_unit.any(np.floor(age) <= p.ages.child_max)
        disabled = spm_unit.any(person("is_disabled", period))
        veteran = spm_unit.any(person("is_veteran", period))
        # The plan measures home-energy utilities; aggregate existing energy
        # bills, excluding water/sewer/trash/phone. Annual expenses approximate
        # current monthly bills, and rent-embedded charges are not available.
        cost = add(spm_unit, period, p.energy_cost_sources)
        high_burden = (cost > 0) & (cost >= income * p.burden_rate)
        fuel = spm_unit("heating_type", period)
        fuel_supplement = np.isin(fuel.decode_to_str(), p.supplement_fuels)
        a = p.amounts
        amount = (
            a.base
            + a.elderly * elderly
            + a.child * child
            + a.disabled * disabled
            + a.veteran * veteran
            + a.low_income * low_income
            + a.high_burden * high_burden
            + a.fuel * fuel_supplement
        )
        eligible = spm_unit("sc_liheap_eligible", period)
        # Local funding and priority decisions are not represented. The state
        # schedule does not impose a general benefit-to-bill cap.
        return where(eligible, min_(amount, a.maximum), 0)
