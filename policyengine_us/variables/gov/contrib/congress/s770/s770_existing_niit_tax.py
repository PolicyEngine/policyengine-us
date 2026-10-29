from policyengine_us.model_api import *
from policyengine_us.reforms.congress.s770.section_8 import (
    enabled,
    allocate_bases,
    revenue_shares,
)


class s770_existing_niit_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Existing NIIT rate on the S.770 NII allocation"
    documentation = "This component is included in net_investment_income_tax when the structural reform is enabled. Missing passive pass-through data understate NII and overstate active income until the Microcosm entity/passive field repairs are present. See the reform README for statutory category and NOL limitations."
    unit = USD
    definition_period = YEAR
    reference = "https://www.congress.gov/bill/119th-congress/senate-bill/770/text"

    def formula(tax_unit, period, parameters):
        rate = parameters(period).gov.irs.investment.net_investment_income_tax.rate
        return rate * tax_unit("s770_nii_taxable_base", period)
