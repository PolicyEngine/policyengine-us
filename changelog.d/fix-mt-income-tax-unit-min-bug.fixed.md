Fixed MT state_income_tax returning $0 for 2024+ by replacing min_(indiv, joint) with where(filing_separately, indiv, joint) in mt_income_tax_before_refundable_credits_unit.
