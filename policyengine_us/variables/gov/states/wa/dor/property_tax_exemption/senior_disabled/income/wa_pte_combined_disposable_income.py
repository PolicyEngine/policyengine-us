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
        # RCW 84.36.383(2) combines the disposable income of the claimant,
        # the spouse or domestic partner, and each cotenant occupying the
        # residence. WAC 458-16A-120(2)(b) adds each item left out of AGI to
        # the AGI of the person who received it, so a tax unit dependent's
        # benefits, pensions, military pay and tax-exempt interest are the
        # dependent's own. Person-level sources are summed over the head and
        # spouse; AGI and filer_tax_exempt_social_security already describe
        # their return. Other cotenants, including a tax unit dependent who
        # owns part of the residence, come in through
        # wa_pte_cotenant_disposable_income.
        own_income = tax_unit_non_dep_add(tax_unit, period, p.sources)
        cotenant_income = tax_unit("wa_pte_cotenant_disposable_income", period)
        income = own_income + cotenant_income
        # The deductions are amounts the claimant or spouse paid (RCW
        # 84.36.383(2)). Expense inputs record whose expense it is, not who
        # paid it, so they are summed over every tax unit member.
        itemized = add(tax_unit, period, p.deductions.sources)
        # ESSB 6162 (RCW 84.36.383(14)) lets the claimant elect the standard
        # deduction in place of the itemized medical basket. The per-claimant
        # amount applies once, plus an additional amount if filing jointly
        # (proxying spouse or domestic partner cohabitation).
        is_joint = tax_unit("tax_unit_is_joint", period)
        standard = p.deductions.standard_amount * (1 + is_joint)
        return income - max_(itemized, standard)
