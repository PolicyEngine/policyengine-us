from policyengine_us.model_api import *


class pa_liheap_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Pennsylvania LIHEAP annual countable household income"
    defined_for = StateCode.PA
    reference = (
        # Sections 601.81-601.84, physical pages 49-54 and 46-51 respectively.
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dhs/documents/services/assistance/documents/heating-assistance_liheap/2026-liheap-state-plan.pdf#page=49",
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dhs/documents/services/assistance/documents/heating-assistance_liheap/2027-liheap-state-plan.pdf#page=46",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.pa.dhs.liheap.income
        person = spm_unit.members
        wages = add(spm_unit, period, ["pa_liheap_countable_employment_income"])
        business = 0
        for source in p.sources.business:
            # Section 601.82(2)(ii) forbids one source's loss offsetting another.
            # Keep existing net inputs without a second business-cost deduction.
            business = business + max_(person(source, period), 0)
        unearned = add(spm_unit, period, p.sources.unearned, options=[ADD])
        # The state TANF grant is counted once. Its default formula estimates
        # an eligible grant; an observed award can override the existing input.
        # Rental inputs are assumed nonnegative. Business and unearned income
        # of dependent children count, as does nonqualified members' income.
        children = spm_unit.sum(person("age", period) < p.child_age_limit)
        child_support = add(spm_unit, period, ["child_support_received"])
        alimony = add(spm_unit, period, ["alimony_income"])
        child_exclusion = min_(
            child_support,
            p.support.monthly_child_disregard.calc(children) * MONTHS_IN_YEAR,
        )
        spousal_exclusion = min_(
            alimony, p.support.monthly_spousal_disregard * MONTHS_IN_YEAR
        )
        # Under the annual steady-receipt approximation, only the larger of
        # the child and spousal exclusions applies, not the sum of both caps.
        support_exclusion = max_(child_exclusion, spousal_exclusion)
        # Annual income does not reproduce the applicant's prior-month election.
        # Gross SSA overstates counted income where Medicare premiums apply;
        # that deduction is deferred. Financial assistance counts cash help
        # from friends or relatives. Existing inputs cannot fully identify
        # direct utility allowances, CD/stock-sale proceeds, same-household
        # support/rent, or refunded support. Capital gains cannot proxy proceeds.
        return max_(wages + spm_unit.sum(business) + unearned - support_exclusion, 0)
