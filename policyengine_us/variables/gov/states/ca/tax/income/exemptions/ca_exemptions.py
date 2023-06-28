from policyengine_us.model_api import *


class ca_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "CA Exemptions"
    defined_for = StateCode.CA
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
        exemption_reduction = increments * p.phase_out.amount

        # Personal Exemptions
        personal_exemption_count = p.personal_scale[filing_status]
        personal_aged_blind_exemption_count = (
            personal_exemption_count + tax_unit("aged_blind_count", period)
        )
        personal_aged_blind_exemption = max_(
            0,
            personal_aged_blind_exemption_count
            * (p.amount - exemption_reduction),
        )

        # Dependent exemptions
        dependents = tax_unit("tax_unit_dependents", period)
        dependent_exemptions = max_(
            0, dependents * (p.dependent_amount - exemption_reduction)
        )

        # total exemptions
        return personal_aged_blind_exemption + dependent_exemptions
