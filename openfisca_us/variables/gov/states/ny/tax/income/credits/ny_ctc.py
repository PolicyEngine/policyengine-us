from openfisca_us.model_api import *


class ny_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY CTC"
    documentation = "New York's Empire State Child Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (c-1)

    def formula(tax_unit, period, parameters):
        in_ny = tax_unit.household("state_code_str", period) == "NY"
        p = parameters(period).states.ny.tax.income.credits.refundable.ctc
        # Qualifying children.
        person = tax_unit.members
        qualifies_for_federal_ctc = person("is_ctc_qualifying_child", period)
        age = person("age", period)
        qualifies = qualifies_for_federal_ctc & (age >= p.minimum_age)
        qualifying_children = tax_unit.sum(qualifies)
        # First calculate federal match.
        federal_match = tax_unit("ctc", period) * p.amount.percent
        # Scale federal match by number of qualifying children.
        federal_qualifying_children = tax_unit.sum(qualifies_for_federal_ctc)
        qualifying_federal_match = (
            federal_match * qualifying_children / federal_qualifying_children
        )
        # Filers with income below the CTC phase-out threshold receive a
        # minimum amount per child.
        minimum = p.amount.minimum * qualifying_children
        agi = tax_unit("adjusted_gross_income", period)
        federal_threshold = tax_unit("ctc_phase_out_threshold", period)
        eligible_for_minimum = agi < federal_threshold
        applicable_minimum = eligible_for_minimum * minimum
        eligible = in_ny & (qualifying_children > 0)
        return eligible * max_(applicable_minimum, qualifying_federal_match)
