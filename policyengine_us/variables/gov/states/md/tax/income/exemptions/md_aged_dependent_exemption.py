from policyengine_us.model_api import *


class md_aged_dependent_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD aged dependent exemption"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://govt.westlaw.com/mdc/Document/NF59A76006EA511E8ABBEE50DE853DFF4?viewType=FullText&originationContext=documenttoc&transitionType=CategoryPageItem&contextData=(sc.Default)",
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-211&enactments=false",
        # Exemption amount chart (10A).
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=12",
    )
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.md.tax.income.exemptions.aged
        # These apply to dependents over the age of 65
        person = tax_unit.members
        dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        elderly = age >= p.age
        # § 10-211(b)(2) counts dependents "as defined in § 152 of the Internal
        # Revenue Code"; under IRC 152(b)(1) a return on which the filer (or,
        # if joint, either spouse) can be claimed has none.
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        aged_dependents = where(
            filer_is_dependent, 0, tax_unit.sum(dependent & elderly)
        )
        # § 10-211(c) limits "the amount allowed for each exemption under
        # subsection (b)(1) or (2)" by federal AGI, the same limit as the
        # personal exemption; the chart's "reduction applies to the additional
        # dependency exemptions as well".
        per_exemption = tax_unit("md_personal_exemption", period)
        return aged_dependents * min_(p.aged_dependent, per_exemption)
