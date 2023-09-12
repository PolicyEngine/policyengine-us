from policyengine_us.model_api import *


class vt_other_retirement_pay_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Vermont allowed other system's retirement income exclusion"
    reference = (
        "https://tax.vermont.gov/individuals/seniors-and-retirees",
        "https://legislature.vermont.gov/statutes/section/32/151/05830e",  # Legal Code Titl. 32 V.S.A. § 5830e (c)
    )
    unit = USD
    defined_for = StateCode.VT
    documentation = "Vermont allowed other system's retirement benefits exempt from Vermont taxation."

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(
            period
        ).gov.states.vt.tax.income.agi.retirement_income_exemption
        # Get retirement amount from military retirement system
        tax_unit_other_retirement_pay = tax_unit.sum(
            person("vt_other_retirement_pay", period)
        )
        # Retirement income from systems other than social security have maximum amount and assume that filers will always choose the largest one
        return min_(tax_unit_other_retirement_pay, p.cap)
