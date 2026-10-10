from policyengine_us.model_api import *


class in_base_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana base exemptions"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5",  # (a)(3)-(4)
        # Information Bulletin 117: the filer's own exemption is allowed "even
        # if the individual can be claimed as a dependent", while dependents
        # follow federal rules.
        "https://www.in.gov/dor/files/ib117.pdf#page=2",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["in"].tax.income.exemptions
        size = tax_unit("tax_unit_size", period)
        dependents = tax_unit("tax_unit_dependents", period)
        # Each filer keeps the $1,000 exemption even when another taxpayer can
        # claim them, but a return on which the filer (or, if joint, either
        # spouse) can be claimed as a dependent has no dependents (IRC
        # 152(b)(1)).
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        exemptions = where(filer_is_dependent, size - dependents, size)
        return exemptions * p.base.amount
