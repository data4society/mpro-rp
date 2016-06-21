#encoding "utf-8"

Loc1 -> Word<gram='geo'>;
Loc2 -> Word<kwtype='location_front'> Word<h-reg1>;
Loc3 -> Word<h-reg1> Word<kwtype='location_back'>;
Loc4 -> Word<kwtype='abbreviation'> Word<h-reg1>;

Loc -> Loc1 | Loc2 | Loc3 | Loc4;
Location -> Loc interp(LocationFact_TOMITA.Loc_TOMITA::not_norm);