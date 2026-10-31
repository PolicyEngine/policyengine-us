# Social Security scoring data preflight

Audit the actual stored dataset before scoring Social Security reform levers:

```bash
python -m policyengine_us.tools.social_security_preflight /path/to/populace_us_2024.h5 > receipt.json
```

The defaults identify the certified 2024 artifact
`hf://datasets/policyengine/populace-us/populace_us_2024.h5@populace-us-2024-spm-20260909`
and require SHA256
`6496cc4393d4d3c6574f76eca231de5898c803b9067645591fd5c4d3e65aee84`.
An alternative artifact requires its own `--artifact`, `--year` and `--sha256`.
The preflight reads the H5's stored year and entity column metadata, without
calculating model outputs or loading the entity rows.

Each of retirement, disability, survivors and dependents must have exactly one
Person source: its original public column name or its `_reported` input name.
The receipt records the source mapping that the PE-US constructor must implement.
Two names for one component would retain a final public override and are rejected.
Stored aggregate `social_security`, OASDI payroll-tax outputs, federal NIIT
liabilities/revenues and TOB revenue outputs are also rejected: these would bypass
the formulas being scored. The preflight also rejects the S.770 section 8 and
owners' draw tax and OASDI transfer leaves and the
[OASDI accounting outputs](social-security-oasdi-accounting.md); their
classification inputs remain valid sources. This population-data contract permits
household situations to continue using explicit final benefit overrides.

The JSON receipt records the artifact, hash, base year, stored H5 keys, complete
column inventory by entity, row counts, source mapping and any declared final
overrides. The Python function also accepts `intentional_final_overrides` so a
scoring caller can record its other overrides; final benefit and affected tax
overrides are rejected. The receipt applies to those exact bytes and that
declared override set. Constructor integration tests separately verify that each
legacy component source is migrated once.

Use `extend_single_year_dataset` explicitly through the scoring horizon (2035 by
default; change the recorded horizon with `--projection-end-year`). Its projected
rows are independent annual cross-sections. Reconstruct retirement eligibility
within each scoring year as `payment_year - age + 62` when authoritative inputs
are unavailable. Thus a row aged 70 implies 2018 eligibility in a 2026 score and
2027 eligibility in a 2035 score. Integer ages leave a one-year birthday ambiguity.
Do not carry inferred eligibility, claiming, entitlement or prior-income histories
between projected rows; report the relevant proxy sensitivities with the score.
