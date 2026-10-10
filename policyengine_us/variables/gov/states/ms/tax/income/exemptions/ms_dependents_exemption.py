from policyengine_us.model_api import *


class ms_dependents_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi qualified and other dependent children exemption"
    reference = (
        "https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80100221.pdf#page=5",
        "https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80100251%202.pdf#page=6",
        "https://www.sos.ms.gov/adminsearch/ACCode/00000158c.pdf#page=115",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )
    definition_period = YEAR
    defined_for = StateCode.MS

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ms.tax.income.exemptions.dependents
        # Miss. Code 27-7-21(e) allows the exemption for each person who
        # "qualifies for federal income tax purposes as a dependent of the
        # taxpayer" (Form 80-100 instructions). Under IRC 152(b)(1) a return
        # on which the filer, or on a joint return either spouse, can be
        # claimed as a dependent has no dependents; the filers keep their own
        # regular, aged and blind exemptions.
        dependents = tax_unit("tax_unit_dependents", period)
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        return where(filer_is_dependent, 0, dependents) * p.amount
