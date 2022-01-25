from openfisca_us.model_api import *
from openfisca_us.variables.irs.credits.child_tax_credit.maximum import ctc_individual_maximum


class ctc_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "CTC reduction from income"
    unit = "currency-USD"
    documentation = "Reduction of the total CTC due to income."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        income = tax_unit("adjusted_gross_income", period)
        ctc = parameters(period).irs.credits.child_tax_credit
        mars = tax_unit("mars", period)
        income_over_threshold = max_(0, income - ctc.phaseout.original.threshold[mars])
        reduction = ctc.phaseout.rate * income_over_threshold
        maximum_ctc = tax_unit("ctc_maximum", period)
        return min_(reduction, maximum_ctc)

    # TCJA's phaseout changes are purely parametric so don't require structural reform.

    def formula_2021(tax_unit, period, parameters):
        income = tax_unit("adjusted_gross_income", period)
        ctc = parameters(period).irs.credits.child_tax_credit
        mars = tax_unit("mars", period)
        income_over_threshold = max_(0, income - ctc.phaseout.original.threshold[mars])
        reduction = ctc.phaseout.rate * income_over_threshold
        maximum_ctc = tax_unit("ctc_maximum", period)
        original_phaseout = min_(reduction, maximum_ctc)

        income_over_arpa_threshold = max_(0, income - ctc.phaseout.arpa.threshold[mars])
        arpa_phaseout_max_reduction = ctc.phaseout.arpa.rate * income_over_arpa_threshold
        
        no_arpa_parameters = parameters.clone()
        old_ctc = parameters(period.last_year).irs.credits.child_tax_credit
        no_arpa_ctc = no_arpa_parameters.irs.credits.child_tax_credit
        no_arpa_ctc.child.young.increase.update(value=0, period=period)
        no_arpa_ctc.child.amount.update(value=old_ctc.child.amount, period=period)

        ctc_without_arpa = tax_unit.sum(ctc_individual_maximum.formula_2018(tax_unit.members, period, no_arpa_parameters))

        arpa_increase = maximum_ctc - ctc_without_arpa

        arpa_phaseout_range = ctc.phaseout.original.threshold[mars] - ctc.phaseout.arpa.threshold[mars]

        arpa_reduction_max = min_(
            arpa_increase,
            ctc.phaseout.arpa.rate * arpa_phaseout_range,
        )

        arpa_reduction = min_(arpa_phaseout_max_reduction, arpa_reduction_max)

        return original_phaseout + arpa_reduction
    
    formula_2022 = formula
    

