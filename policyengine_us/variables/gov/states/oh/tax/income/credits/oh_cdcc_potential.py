from policyengine_us.model_api import *


class oh_cdcc_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio child and dependent care credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5747.054",
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=20",
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.oh.tax.income.credits.cdcc

        agi = tax_unit("oh_modified_agi", period)
        # ORC § 5747.054(A): filers with AGI below the low-income threshold
        # receive credit "without regard to any limitation imposed by section 26
        # of the Internal Revenue Code", i.e. cdcc_potential.
        # Filers in the middle bracket use cdcc (limited by IRC § 26).
        low_income = agi < p.low_income_threshold
        us_cdcc = where(
            low_income,
            tax_unit("cdcc_potential", period),
            tax_unit("cdcc", period),
        )

        rate = p.match.calc(agi)
        # qualify for full CDCC amount when AGI < 20_000
        # qualify for 25% of CDCC when 20000 <= AGI < 40_000
        # not qualify when AGI >= 40_000
        return rate * us_cdcc
