#encoding "utf-8"

Loc1 -> Word<gram='~persn', gram='geo', no_hom>;
Loc2 -> Word<kwtype='location_front'> Word<h-reg1>;
Loc3 -> Word<h-reg1> Word<kwtype='location_back'>;
Loc4 -> Word<kwtype='abbreviation'> Word<h-reg1>;

Loc -> Loc1<~quoted> | Loc2<~quoted> | Loc3<~quoted> | Loc4<~quoted>;
Location -> Loc interp(LocationFact_TOMITA.Loc_TOMITA::not_norm);