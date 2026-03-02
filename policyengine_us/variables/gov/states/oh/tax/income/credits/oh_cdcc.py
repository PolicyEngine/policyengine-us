from policyengine_us.model_api import *


class oh_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio child and dependent care credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=20",
        "https://codes.ohio.gov/ohio-revised-code/section-5747.054",
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.oh.tax.income.credits.cdcc

        agi = tax_unit("oh_modified_agi", period)
        # Per ORC 5747.054:
        # For AGI < $20,000: 100% of the federal credit without
        # regard to section 26 limitation (i.e., the potential
        # credit before the tax liability cap).
        # For $20,000 <= AGI < $40,000: 25% of the federal credit
        # (with section 26 limitation applied).
        # For AGI >= $40,000: no credit.
        cdcc_potential = tax_unit("cdcc_potential", period)
        cdcc_actual = tax_unit("cdcc", period)
        low_income_threshold = p.low_income_threshold
        us_cdcc = where(
            agi < low_income_threshold,
            cdcc_potential,
            cdcc_actual,
        )

        rate = p.match.calc(agi)
        return rate * us_cdcc
