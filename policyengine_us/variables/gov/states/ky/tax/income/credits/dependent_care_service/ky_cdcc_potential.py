from policyengine_us.model_api import *


class ky_cdcc_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky household and dependent care service credit"
    unit = USD
    definition_period = YEAR
    reference = "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=29058"
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        # Kentucky matches the federal credit taken. KRS 141.067 sets the credit
        # at 20% of "the federal credit allowed under Section 21 of the Internal
        # Revenue Code," and KRS 141.010(21) fixes Kentucky's IRC at the Code in
        # effect on December 31, 2024. From 2026 that frozen Code excludes the
        # OBBBA section 21 rate increase (effective for tax years beginning after
        # 2025-12-31), so Kentucky uses the pre-OBBBA federal credit.
        if period.start.year >= 2026:
            dependent_care_credit = tax_unit("pre_obbba_cdcc", period)
        else:
            dependent_care_credit = tax_unit("cdcc", period)
        rate = parameters(
            period
        ).gov.states.ky.tax.income.credits.dependent_care_service.match
        return dependent_care_credit * rate
