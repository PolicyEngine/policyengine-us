from policyengine_us.model_api import *


class vt_csrs_retirement_pay_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Vermont Civil Service Retirement System (CSRS) retirement income exclusion"
    reference = (
        "https://tax.vermont.gov/individuals/seniors-and-retirees",
        "https://legislature.vermont.gov/statutes/section/32/151/05830e",  # Legal Code Titl. 32 V.S.A. § 5830e (b)(1)(B), (b)(2)(B)
    )
    unit = USD
    defined_for = StateCode.VT
    documentation = "Vermont Civil Service Retirement System (CSRS) retirement benefits exempt from Vermont taxation."

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(
            period
        ).gov.states.vt.tax.income.agi.retirement_income_exemption.csrs
        # Get retirement amount from military retirement system
        tax_unit_csrs_retirement_pay = add(
            tax_unit, period, ["csrs_retirement_pay"]
        )
        # Retirement income from systems other than social security have maximum amount.
        return min_(tax_unit_csrs_retirement_pay, p.amount)
