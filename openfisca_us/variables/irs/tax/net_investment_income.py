from openfisca_us.model_api import *


class niit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Net Investment Income Tax"
    reference = "https://www.law.cornell.edu/uscode/text/26/1411"
    unit = USD

    def formula(tax_unit, period, parameters):
        NII_ELEMENTS = [
            "filer_e00300",
            "filer_e00600",
            "c01000",
            "filer_e02000",
        ]
        nii = max_(0, add(tax_unit, period, NII_ELEMENTS))
        niit = parameters(period).irs.investment.net_inv_inc_tax
        threshold = niit.threshold[tax_unit("mars", period)]
        base = min_(nii, max_(0, tax_unit("c00100", period) - threshold))
        return niit.rate * base
