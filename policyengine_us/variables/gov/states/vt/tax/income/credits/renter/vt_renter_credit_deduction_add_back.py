from policyengine_us.model_api import *


class vt_renter_credit_deduction_add_back(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont renter credit above-the-line deduction add-back"
    unit = USD
    documentation = (
        "The federal above-the-line deductions that 32 V.S.A. 6061(18)(D) "
        "adds back to federal adjusted gross income for the renter credit, "
        "to the extent this return deducted them."
    )
    definition_period = YEAR
    reference = (
        "https://legislature.vermont.gov/statutes/section/32/154/06061",  # (18)(D)
        "https://tax.vermont.gov/sites/tax/files/documents/RCC-146-2025.pdf#page=1",  # line 10
    )
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.vt.tax.income.credits.renter
        ald = parameters(period).gov.irs.ald
        # "To the extent excluded from federal adjusted gross income": only
        # deductions on this year's federal list, summed as
        # above_the_line_deductions sums them, so a dependent's own
        # deductions, which are on the dependent's return, stay out.
        deductions = [
            deduction
            for deduction in p.deduction_add_backs
            if deduction in ald.deductions
        ]
        return tax_unit_non_dep_add(
            tax_unit,
            period,
            deductions,
            include_dependents=ald.filer_amounts_recorded_on_dependents,
        )
