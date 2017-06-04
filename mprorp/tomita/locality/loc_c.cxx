#encoding "utf-8"

//Loc
Loc -> Word<h-reg1, kwtype='City', kwset=~["FIO"]>;
Location -> Loc<~quoted, ~l-quoted, ~r-quoted> interp(CityFact_TOMITA.Location_TOMITA::not_norm);