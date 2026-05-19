from policyengine_us.model_api import *


class wa_pte_combined_disposable_income(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    definition_period = YEAR
    label = (
        "Washington Senior/Disabled Property Tax Exemption combined disposable income"
    )
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/RCW/default.aspx?cite=84.36.383",
        "https://app.leg.wa.gov/WAC/default.aspx?cite=458-16A-120",
        "https://dor.wa.gov/sites/default/files/2022-02/PTExemption_Senior.pdf#page=2",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.wa.dor.property_tax_exemption.senior_disabled.income
        # RCW 84.36.383(2) requires combining the claimant's, spouse's, and
        # each occupying cotenant's disposable income. AGI (and the other
        # tax-unit-level sources) already excludes dependents because
        # irs_gross_income masks them out at the person level. Non-tax-unit
        # cotenants come in through wa_pte_cotenant_disposable_income.
        # Person-level income add-backs (pension, military pay, veterans
        # benefits) and medical deductions are summed across all tax-unit
        # members. The statute (RCW 84.36.383(2) and (7)) restricts these
        # to amounts of the claimant and spouse/domestic partner only, but
        # we don't filter dependents at the moment.
        own_income = add(tax_unit, period, p.sources)
        cotenant_income = tax_unit("wa_pte_cotenant_disposable_income", period)
        income = own_income + cotenant_income
        itemized = add(tax_unit, period, p.deductions.sources)
        # ESSB 6162 (RCW 84.36.383(14)) lets the claimant elect the standard
        # deduction in place of the itemized medical basket. The per-claimant
        # amount applies once, plus an additional amount if filing jointly
        # (proxying spouse or domestic partner cohabitation).
        is_joint = tax_unit("tax_unit_is_joint", period)
        standard = p.deductions.standard_amount * (1 + is_joint)
        return income - max_(itemized, standard)
