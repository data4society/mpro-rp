#encoding "utf-8"

//Loc
City -> Word<h-reg1, kwtype='city', kwset=~["FIO"]>;
Location -> City<~quoted, ~l-quoted, ~r-quoted> interp(CityFact_TOMITA.City_TOMITA::not_norm);

//Jail
Jail1 -> Word<h-reg1, kwtype='Jail1'> | Word<h-reg1, kwtype='Jail1'> AnyWord<wfl="[)(]*"> Word<h-reg1, kwtype='Jail3'>;
Jail2 -> Word<h-reg1, kwtype='Jail2'>;
Jail3 -> Word<h-reg1, kwtype='Jail3'> | Word<kwtype='Jail4'> AnyWord<wfl="[)(]*"> Word<h-reg1, kwtype='Jail3'>;
Jail4 -> Word<kwtype='Jail4'> '№' AnyWord<wfl="[0-9]+"> | Word<kwtype='Jail4'>;
Jail -> Jail1 | Jail2 | Jail3 | Jail4;
Jail_MAIN -> Jail interp(JailFact_TOMITA.Jail_TOMITA::not_norm);

Main -> Location | Jail_MAIN;