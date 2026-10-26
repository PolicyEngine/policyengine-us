These are public CA certificates, with no private keys. The two affected roots
are listed in the incident's [root inventory](https://emudhra.we-have-a-problem.com/roots.json).
The unaffected emSign G1 root checks that the guard preserves other CA trust.
Tests load real certificates through OpenSSL; they need neither network access
nor a PolicyEngine model.
