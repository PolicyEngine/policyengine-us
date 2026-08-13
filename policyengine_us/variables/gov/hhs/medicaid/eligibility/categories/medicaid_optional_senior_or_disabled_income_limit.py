from policyengine_us.model_api import *


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
    )

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        is_joint = tax_unit("tax_unit_is_joint", period)
        state = person.household("state_code_str", period)

        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.senior_or_disabled

        limit_pct = where(
            is_joint,
            p.income.limit.couple[state],
            p.income.limit.individual[state],
        )
        # Missouri MHABD tests eligibility based on blindness against a
        # higher share of the poverty guideline than eligibility based on
        # old age or permanent and total disability.
        mo_mhabd = parameters(period).gov.states.mo.dss.mhabd.income_limit
        state_code = person.household("state_code", period)
        is_blind = person("is_blind", period)
        limit_pct = where(
            (state_code == StateCode.MO) & is_blind,
            mo_mhabd.blind,
            limit_pct,
        )
        return limit_pct * tax_unit("tax_unit_fpg", period)
