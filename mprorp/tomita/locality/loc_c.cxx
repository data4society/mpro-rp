#encoding "utf-8"

//Loc
City -> Word<h-reg1, kwtype='City', kwset=~["FIO"]>;
Location -> City<~quoted, ~l-quoted, ~r-quoted> AnyWord<kwset=~["Area"]> interp(CityFact_TOMITA.Location_TOMITA::not_norm);