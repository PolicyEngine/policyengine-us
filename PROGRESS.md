# PR B progress — CPUC housing subsidy source + dataset/default/batch guards

Branch: `max/cpuc-housing-and-guards-20260914` (from `upstream/main`, 2.0.1).
Source review: `rollout/fable-continuation-20260911/out/astra-review-country-201.md`.

## State

Scoping complete; implementation not started.

## Done

- Read the Astra review and located every touchpoint:
  - `policyengine_us/parameters/gov/states/ca/cpuc/income_sources.yaml:39` lists
    `spm_unit_capped_housing_subsidy` under "Housing subsidies".
  - `policyengine_us/variables/gov/states/ca/cpuc/ca_cpuc_countable_income.py` is a
    Household variable with `adds = "gov.states.ca.cpuc.income_sources"`; the
    replacement `housing_assistance` is SPMUnit-entity, same as the current entry.
  - `policyengine_us/spm.py:~343` `set_input` guard rejects only
    `FORMULA_OWNED_INPUTS` (calculator side), which already covers `poverty_line`,
    `poverty_gap`, `spm_unit_is_in_spm_poverty`, `spm_unit_is_in_deep_spm_poverty`
    but omits `in_poverty`, `in_deep_poverty`, `deep_poverty_line`,
    `deep_poverty_gap` (all four exist as country SPMUnit variables).
  - `policyengine_us/system.py:55` `DEFAULT_DATASET` pins a HF tag;
    `_resolve_dataset_path` performs no hash check.
  - `policyengine_us/tests/test_batched.py:~575` treats "no N failed" as success and
    terminates the child before reading its exit status; `.yml` is not enumerated
    in `subdir_batches`/`split_into_batches`.
- `uv sync --extra dev` green; `.venv` usable.

## Next

1. Verify the CPUC/PG&E source wording (exact quotation + URL).
2. Swap the parameter entry, update description/reference, add the geography
   independence test, re-run CA CPUC YAML + partner CA fixtures.
3. Dataset guard alias list + test.
4. Default dataset sha256 check + monkeypatched test.
5. Batch runner exit status + `.yml` enumeration + code_health tests.
6. Changelog fragments, `make format`, suites, draft PR.
