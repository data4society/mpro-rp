#encoding "utf-8"

//Loc
City -> Word<h-reg1, kwtype='City'>;
Location -> City<~quoted, ~l-quoted, ~r-quoted> interp(CityFact_TOMITA.City_TOMITA::not_norm);

//Court
Court_Name -> Word<kwset=["Court_R", "Court_O", "Court_G", "Court_K"]>;
Type -> Word<kwtype='Type'>;
Court -> Court_Name Type* Word<kwtype='Court'> | Word<kwtype="Court_Else">;
Court_Main -> Court interp(CourtFact_TOMITA.Court_TOMITA::not_norm);

Main -> Location | Court_Main;