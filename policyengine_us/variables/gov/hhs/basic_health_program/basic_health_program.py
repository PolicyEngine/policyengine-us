from policyengine_us.model_api import *


class basic_health_program(Variable):
    value_type = float
    entity = TaxUnit
    label = "Basic Health Program"
    unit = USD
    definition_period = YEAR
    reference = "https://www.medicaid.gov/basic-health-program"
    defined_for = "basic_health_program_tax_unit_enrolled"
    documentation = (
        "Initial BHP payment proxy using the 2026 CMS federal funding "
        "methodology: the adjusted reference premium minus the household "
        "contribution amount, multiplied by the income reconciliation factor "
        "and 95 percent federal payment rate. The CSR component is currently "
        "modeled as zero because CMS assigns the CSR payment portion a zero "
        "value while there is no available CSR appropriation."
    )

    def formula(tax_unit, period, parameters):
        return 0

    def formula_2026(tax_unit, period, parameters):
        p = parameters(period).gov.hhs.basic_health_program.payment
        magi_fraction = tax_unit("aca_magi_fraction", period)
        ptc_income_eligible = parameters(period).gov.aca.ptc_income_eligibility.calc(
            magi_fraction
        )
        adjusted_reference_premium = tax_unit(
            "basic_health_program_adjusted_reference_premium", period
        )
        contribution = tax_unit("aca_magi", period) * tax_unit(
            "aca_required_contribution_percentage", period
        )
        ptc_component = where(
            ptc_income_eligible,
            max_(0, adjusted_reference_premium - contribution),
            0,
        )
        return ptc_component * p.income_reconciliation_factor * p.federal_payment_rate
