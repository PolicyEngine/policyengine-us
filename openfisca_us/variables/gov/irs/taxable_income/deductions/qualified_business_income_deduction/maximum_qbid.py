from openfisca_us.model_api import *


class maximum_qbid(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maximum qualified business income deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/199A#b_2"

    def formula(tax_unit, period, parameters):
        qbi = tax_unit("qualified_business_income", period)
        w2_wages = tax_unit("w2_wages_from_qualified_business", period)
        qualified_property = tax_unit("unadjusted_basis_qualified_property", period)
        qbid = parameters(period).irs.deductions.qbi
        return min_(
            qbid.max.rate * qbi,
            max_(
                qbid.max.w2_wages.rate * w2_wages,
                (
                    qbid.max.w2_wages.alt_rate * w2_wages
                    + qbid.max.business_property.rate * qualified_property
                )
            )
        )