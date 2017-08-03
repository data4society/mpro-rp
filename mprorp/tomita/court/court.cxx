#encoding "utf-8"


Court_Name -> Word<kwset=["Court_R", "Court_O", "Court_G", "Court_K"]>;

Type -> Word<kwtype='Type'>;

Court -> Court_Name Type* Word<kwtype='Court'> | Word<kwtype="Court_Else">;

Court_Main -> Court  interp(CourtFact_TOMITA.Court_TOMITA::not_norm);