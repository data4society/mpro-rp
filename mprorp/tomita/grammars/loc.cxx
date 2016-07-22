#encoding "utf-8"

Loc1 -> Word<gram='~persn', gram='geo', no_hom>;
Loc2 -> Word<kwtype='location_front'> Word<h-reg1>;
Loc3 -> Word<h-reg1> Word<kwtype='location_back'>;
Loc4 -> Word<kwtype='abbreviation'> Word<h-reg1>;
Loc5 -> Word<kwtype='lost_loc'>;

Loc -> Loc1<~l-quoted, ~r-quoted> | Loc2<~l-quoted, ~r-quoted> | Loc3<~l-quoted, ~r-quoted> | Loc4<~l-quoted, ~r-quoted> | Loc5<~l-quoted, ~r-quoted>;
Location -> Loc interp(LocationFact_TOMITA.Loc_TOMITA::not_norm);