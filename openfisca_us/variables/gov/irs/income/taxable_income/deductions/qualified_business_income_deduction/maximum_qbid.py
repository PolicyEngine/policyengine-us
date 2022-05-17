from openfisca_us.model_api import *


class maximum_qbid(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maximum qualified business income deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/199A#b_2"

    def formula(tax_unit, period, parameters):
        qbi = add(tax_unit, period, ["qualified_business_income"])
        qbid = parameters(period).irs.deductions.qbi
        return qbid.max.rate * qbi
