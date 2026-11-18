from policyengine_us.model_api import *


class nyc_cdcc_age_restricted_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Childcare expenses for children under NYC CDCC age limit"
    unit = USD
    definition_period = YEAR
    defined_for = "in_nyc"

    def formula(tax_unit, period, parameters):
        # For now define this as total childcare expenses times
        # the share of children in the tax unit under the NYC CDCC age limit.

        # Get the CDCC parameter tree.
        p = parameters(period).gov.local.ny.nyc.tax.income.credits.cdcc

        children = tax_unit("tax_unit_children", period)
        person = tax_unit.members
        # NYC Admin Code 11-1706(e)(1) counts children "who are dependents of
        # the taxpayer"; a return on which the filer (or, if joint, either
        # spouse) can be claimed as a dependent has none (IRC 152(b)(1)).
        dependent_filer = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
        )
        qualifying_child = (
            person("age", period) < p.child_age_restriction
        ) & ~dependent_filer
        qualifying_children = tax_unit.sum(qualifying_child)
        tax_unit_childcare_expenses = tax_unit("tax_unit_childcare_expenses", period)
        # avoid divide-by-zero warnings by not using where() function
        qualifying_child_share = np.zeros_like(children)
        mask = children > 0
        qualifying_child_share[mask] = qualifying_children[mask] / children[mask]
        return tax_unit_childcare_expenses * qualifying_child_share
