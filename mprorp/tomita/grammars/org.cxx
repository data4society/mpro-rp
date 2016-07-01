#encoding "utf-8"

Trial -> Word<kwtype='trial'>;
OOO -> Word<kwtype='OOO'> Word<h-reg2> | Word<kwtype='OOO'> Word<quoted> | Word<kwtype='OOO'> Word<lat>;

Org -> Trial | OOO;
Organisation -> Org interp(OrgFact_TOMITA.Org_TOMITA::not_norm);