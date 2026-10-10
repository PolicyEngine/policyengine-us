from policyengine_us.model_api import *


class il_dependent_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Illinois dependent exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = (
        # 35 ILCS 5/204(c): an exemption for each exemption "allowable" under
        # IRC 151.
        "https://www.ilga.gov/legislation/ilcs/fulltext.asp?DocName=003500050K204",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )

    def formula(tax_unit, period, parameters):
        amount = parameters(period).gov.states.il.tax.income.exemption.dependent
        # A return on which the filer (or, if joint, either spouse) can be
        # claimed as a dependent has no dependents (IRC 152(b)(1)).
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        dependents = tax_unit("tax_unit_dependents", period)
        return amount * where(filer_is_dependent, 0, dependents)
