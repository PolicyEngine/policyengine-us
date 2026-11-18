from policyengine_us.model_api import *
from policyengine_us.reforms.congress.s770.section_8 import (
    enabled,
    allocate_bases,
    revenue_shares,
)


class s770_nii_taxable_base(Variable):
    value_type = float
    entity = TaxUnit
    label = "S.770 NII allocation of the unified taxable base"
    documentation = "Net signed NII and active income before clipping to the MAGI excess, then allocate to NII first independently of rates. Both allocated bases are nonnegative. The existing NIIT allocation must change with signed active losses. This component is included in net_investment_income_tax when the structural reform is enabled. Missing passive pass-through data understate NII and overstate active income until the Microcosm entity/passive field repairs are present. See the reform README for statutory category and NOL limitations."
    unit = USD
    definition_period = YEAR
    reference = "https://www.congress.gov/bill/119th-congress/senate-bill/770/text"

    def formula(tax_unit, period, parameters):
        p = parameters(period)
        niit = p.gov.irs.investment.net_investment_income_tax
        options = p.gov.contrib.congress.s770.section_8
        excess = (
            tax_unit("niit_magi", period)
            - niit.threshold[tax_unit("filing_status", period)]
        )
        active = (
            tax_unit("s770_active_business_income", period)
            if enabled(options.active_business, period)
            else 0
        )
        return allocate_bases(tax_unit("s770_nii_base", period), active, excess)[0]
