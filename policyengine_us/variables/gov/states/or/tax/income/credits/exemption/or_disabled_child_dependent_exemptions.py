from policyengine_us.model_api import *


class or_disabled_child_dependent_exemptions(Variable):
    value_type = int
    entity = TaxUnit
    label = "OR disabled child dependent exemptions"
    definition_period = YEAR
    reference = (
        "https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2021.pdf#page=17",
        "https://www.oregonlegislature.gov/bills_laws/ors/ors316.html",  # Subsection 316.099(3)
    )
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        # Identify qualifying tax unit members.
        person = tax_unit.members
        disabled = person("is_disabled", period)
        # Law references IRC Section 152, which defines child dependent for EITC.
        eitc_qualifying_child = person("is_qualifying_child_dependent", period)
        # Determine eligibility from AGI.
        federal_agi = tax_unit("adjusted_gross_income", period)
        p = parameters(period).gov.states["or"].tax.income.credits.exemption
        qualifies = federal_agi <= p.income_limit.disabled_child_dependent
        # ORS 316.099 requires "a dependent of the taxpayer"; under IRC
        # 152(b)(1) a return on which the filer (or, if joint, either spouse)
        # can be claimed as a dependent has no dependents.
        dependent_filer = tax_unit(
            "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
        )
        count = tax_unit.sum(eitc_qualifying_child & disabled)
        return qualifies * where(dependent_filer, 0, count)
