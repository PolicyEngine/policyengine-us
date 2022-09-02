from openfisca_us.model_api import *


class ny_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY CTC"
    documentation = "New York's Empire State Child Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (c-1)
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ny.tax.income.credits.ctc
        # Qualifying children.
        person = tax_unit.members
        qualifies_for_federal_ctc = person("is_ctc_qualifying_child", period)
        age = person("age", period)
        qualifies = qualifies_for_federal_ctc & (age >= p.minimum_age)
        qualifying_children = tax_unit.sum(qualifies)
        # First calculate federal match.
        federal_match = tax_unit("ny_federal_ctc", period) * p.amount.percent
        # Scale federal match by number of qualifying children.
        federal_qualifying_children = tax_unit.sum(qualifies_for_federal_ctc)
        qualifying_federal_match = where(
            federal_qualifying_children > 0,
            federal_match * qualifying_children / federal_qualifying_children,
            0,
        )
        # Filers with income below the CTC phase-out threshold receive a
        # minimum amount per child.
        minimum = p.amount.minimum * qualifying_children
        agi = tax_unit("adjusted_gross_income", period)
        ctc = parameters(
            "2017-01-01"
        ).gov.irs.credits.ctc  # Uses pre-TCJA parameters
        filing_status = tax_unit("filing_status", period)
        federal_threshold = ctc.phase_out.threshold[filing_status]
        eligible_for_minimum = agi < federal_threshold
        applicable_minimum = eligible_for_minimum * minimum
        eligible = qualifying_children > 0
        return eligible * max_(applicable_minimum, qualifying_federal_match)
