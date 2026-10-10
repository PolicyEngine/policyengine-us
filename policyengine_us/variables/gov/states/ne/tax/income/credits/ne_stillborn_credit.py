from policyengine_us.model_api import *


class ne_stillborn_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Nebraska stillborn child tax credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NE
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=77-2715.07",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ne.tax.income.credits
        stillborn = tax_unit("tax_unit_stillborn_children", period)
        # Neb. Rev. Stat. 77-2715.07 requires that the child "would have been
        # a dependent of the individual claiming the credit". Under IRC
        # 152(b)(1) a return on which the filer, or on a joint return either
        # spouse, can be claimed as a dependent has no dependents.
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        return where(filer_is_dependent, 0, stillborn) * p.stillborn
