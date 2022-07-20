from openfisca_us.model_api import *
import numpy as np


class ca_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "CA Exemptions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/2021/2021-540.pdf"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.exemptions
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)

        # calculating phase out amount per credit
        over_agi_threshold = max_(0, agi - p.phase_out.start[filing_status])
        increments = np.ceil(
            over_agi_threshold / p.phase_out.increment[filing_status]
        )
        exemption_reduction = increments * p.phase_out.amount[filing_status]

        # Personal Exemptions
        personal_exemption = p.personal_scale[filing_status] * p.amount
        personal_exemption = max_(0, personal_exemption - exemption_reduction)

        # Blind and Senior Exemptions
        aged_blind_count = tax_unit("aged_blind_count", period)
        blind_senior_exemption = aged_blind_count * (
            p.amount - exemption_reduction
        )
        blind_senior_exemption = max_(0, blind_senior_exemption)

        # Dependent exemptions
        person = tax_unit.members
        is_dependent = person("is_tax_unit_dependent", period)
        num_dependent = tax_unit.sum(is_dependent, period)
        dependent_exemptions = num_dependent * (
            p.dependent_amount - exemption_reduction
        )
        dependent_exemptions = max_(0, dependent_exemptions)

        # total exemptions
        exemptions = (
            personal_exemption + blind_senior_exemption + dependent_exemptions
        )

        # eligibility
        in_ca = tax_unit.household("state_code_str", period) == "CA"
        eligibility = in_ca

        return eligibility * exemptions
