from policyengine_us.model_api import *


class ny_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY exemptions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/616"
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        # Tax Law 616(a) gives the exemption for each dependent for whom the
        # taxpayer is entitled to a deduction under IRC 151(c); a return on
        # which the filer (or, if joint, either spouse) can be claimed as a
        # dependent has none (IRC 152(b)(1)).
        dependent_filer = tax_unit(
            "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
        )
        count_dependents = where(
            dependent_filer, 0, tax_unit("tax_unit_child_dependents", period)
        )
        dependent_exemption = parameters(
            period
        ).gov.states.ny.tax.income.exemptions.dependent
        return dependent_exemption * count_dependents
