from policyengine_us.model_api import *


class sc_tanf_gross_unearned_income(Variable):
    value_type = float
    entity = Person
    label = "South Carolina TANF gross unearned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.SC
    # PDF pages 102, 107-120
    reference = "https://dss.sc.gov/media/bxwc1jdj/tanf-policy-manual-volume-67-final.pdf#page=102"  # Sections 7.1 and 7.7

    def formula(person, period, parameters):
        p = parameters(period).gov.states.sc.tanf.income.unearned
        # Section 7.7 excludes the income of SSI recipients.
        counted = ~person("sc_tanf_ssi_recipient", period)
        unearned = add(person, period, p.sources) * counted
        # Section 7.7 excludes up to $400 of interest, dividends and royalties
        # per benefit group each year and averages the rest over 12 months.
        # Each member's exclusion is proportional to their share of that income.
        p_exclusion = p.interest_and_dividends
        interest_and_dividends = (
            max_(add(person, period, p_exclusion.sources), 0) * counted
        )
        unit_interest_and_dividends = person.spm_unit.sum(interest_and_dividends)
        unit_exclusion = min_(
            unit_interest_and_dividends, p_exclusion.exclusion / MONTHS_IN_YEAR
        )
        share = np.divide(
            interest_and_dividends,
            unit_interest_and_dividends,
            out=np.zeros_like(interest_and_dividends),
            where=unit_interest_and_dividends > 0,
        )
        return unearned - unit_exclusion * share
