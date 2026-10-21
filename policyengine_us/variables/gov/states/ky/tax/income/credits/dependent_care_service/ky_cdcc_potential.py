from policyengine_us.model_api import *


class ky_cdcc_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky household and dependent care service credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=29058",
        "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=57913#page=3",
    )
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ky.tax.income
        # Kentucky matches the federal credit taken. KRS 141.067 sets the credit
        # at 20% of "the federal credit allowed under Section 21 of the Internal
        # Revenue Code," and KRS 141.010(21) fixes that Code at a reference
        # date. Where the reference date predates the One Big Beautiful Bill
        # Act, Kentucky's section 21 excludes the Act's rate increase. From
        # 2026 the reference date is December 31, 2025, which includes it.
        # The 2019-2021 reference date (December 31, 2018) also excludes the
        # American Rescue Plan Act's 2021 section 21 expansion (2021 Form
        # 2441-K); the model does not apply that yet, so 2021 reads the live
        # federal credit.
        if p.irc_conformity.obbba:
            federal_credit = tax_unit("cdcc", period)
        else:
            federal_credit = tax_unit("pre_obbba_cdcc", period)
        return federal_credit * p.credits.dependent_care_service.match
