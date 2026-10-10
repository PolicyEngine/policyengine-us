from policyengine_us.model_api import *


class ny_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY CDCC"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/606",  # (c), (c-2)
        "https://www.tax.ny.gov/pdf/current_forms/it/it216i.pdf#page=1",
    )
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ny.tax.income.credits.cdcc.decoupled
        if p.in_effect:
            # Tax Law 606(c-2), for taxable years beginning on or after
            # 2026-01-01: qualifying expenses times the applicable percentage,
            # less $20 per whole $1,000 of New York AGI above $750,000.
            # (c-2)(2)(A) excludes a taxpayer who is another's dependent and,
            # through IRC 21(e)(4), a married taxpayer filing separately. A
            # joint return is one taxpayer, so either spouse being a dependent
            # bars it.
            expenses = tax_unit("ny_cdcc_qualifying_expenses", period)
            rate = tax_unit("ny_cdcc_applicable_percentage", period)
            excess = max_(tax_unit("ny_agi", period) - p.reduction.threshold, 0)
            reduction = p.reduction.amount * np.floor(excess / p.reduction.increment)
            eligible = tax_unit("cdcc_filing_status_eligible", period) & ~tax_unit(
                "head_or_spouse_is_dependent_elsewhere", period
            )
            return eligible * max_(expenses * rate - reduction, 0)
        # Tax Law 606(c), for taxable years beginning before 2026.
        cdcc_max = tax_unit("ny_cdcc_max", period)
        expenses = tax_unit("cdcc_relevant_expenses", period)
        cdcc_rate = tax_unit("ny_cdcc_rate", period) * tax_unit("cdcc_rate", period)
        # Form IT-216 requires qualifying for the federal credit and applies
        # the IRC §21(e)(2) and (4) special rules, so a married filer must
        # file jointly unless treated as unmarried.
        eligible = tax_unit("cdcc_filing_status_eligible", period)
        return eligible * min_(cdcc_max, expenses * cdcc_rate)
