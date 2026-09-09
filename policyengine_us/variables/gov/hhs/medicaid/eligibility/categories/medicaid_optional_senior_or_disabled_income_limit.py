from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class medicaid_optional_senior_or_disabled_income_limit(Variable):
    value_type = float
    entity = Person
    label = (
        "Income limit for a state's optional Medicaid pathway for seniors "
        "or people with disabilities"
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396a#m",
        "https://dssmanuals.mo.gov/mo-healthnet-for-the-aged-blind-and-disabled/0805-000-00/0805-015-00/0805-015-45-income-maximum/",
        "https://dssmanuals.mo.gov/wp-content/uploads/2022/07/mhabd-appendix-j.pdf#page=1",
    )

    def formula(person, period, parameters):
        # Non-MAGI Medicaid follows the SSI financial responsibility rules
        # (42 CFR 435.602): the unit is the individual, or the married
        # couple living together, whatever their filing status.
        is_couple = person.marital_unit.nb_persons() == 2
        state = person.household("state_code_str", period)
        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.senior_or_disabled
        limit_pct = where(
            is_couple,
            p.income.limit.couple[state],
            p.income.limit.individual[state],
        )
        # Missouri MHABD tests eligibility based on blindness against a
        # higher share of the poverty guideline than eligibility based on
        # old age or permanent and total disability.
        mo_mhabd = parameters(period).gov.states.mo.dss.mhabd.income_limit
        is_mo = person.household("state_code", period) == StateCode.MO
        is_blind = person("is_blind", period)
        limit_pct = where(is_mo & is_blind, mo_mhabd.blind, limit_pct)
        state_group = person.household("state_group_str", period)
        unit_fpg = fpg(where(is_couple, 2, 1), state_group, period, parameters)
        # Missouri publishes monthly dollar standards (Appendix J), each the
        # percentage of the monthly guideline rounded up to the next dollar.
        mo_monthly_limit = np.ceil(limit_pct * unit_fpg / MONTHS_IN_YEAR)
        return where(
            is_mo,
            mo_monthly_limit * MONTHS_IN_YEAR,
            limit_pct * unit_fpg,
        )
