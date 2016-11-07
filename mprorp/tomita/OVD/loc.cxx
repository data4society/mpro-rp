#encoding "utf-8"

//Loc
Loc1 -> Word<gram='~persn', gram='geo', no_hom>;
Loc2 -> Word<kwtype='location_front'> Word<h-reg1>;
Loc3 -> Word<h-reg1> Word<kwtype='location_back'>;
Loc4 -> Word<kwtype='abbreviation'> Word<h-reg1>;
Loc5 -> Word<kwtype='lost_loc'>;
Loc6 -> Word<kwtype='city', h-reg1>;

//Other1 -> Prep | Word<gram="CONJ">;
Other1 -> Word<gram="CONJ">;
Other2 -> Other1* Adj<h-reg1>+ | Other1* Noun<h-reg1, wfl=~'ОВД'>+;
Type_3_4 -> Other2+ interp(LocationFact_TOMITA.type_3_4_TOMITA::not_norm) Word<kwtype="type_3_4"> | Word<kwtype="type_3_4"> Other2+ interp(LocationFact_TOMITA.type_3_4_TOMITA::not_norm);
Type_3_4_5 -> Other2+ interp(LocationFact_TOMITA.type_3_4_5_TOMITA::not_norm) Word<kwtype="type_3_4_5"> | Word<kwtype="type_3_4_5"> Other2+ interp(LocationFact_TOMITA.type_3_4_5_TOMITA::not_norm);
Type_1_3_4 -> Other2+ interp(LocationFact_TOMITA.type_1_3_4_TOMITA::not_norm) Word<kwtype="type_1_3_4"> | Word<kwtype="type_1_3_4"> Other2+ interp(LocationFact_TOMITA.type_1_3_4_TOMITA::not_norm);
Type_5 -> Other2+ interp(LocationFact_TOMITA.type_5_TOMITA::not_norm) Word<kwtype="type_5"> | Word<kwtype="type_5"> Other2+ interp(LocationFact_TOMITA.type_5_TOMITA::not_norm);
Type_1 -> Other2+ interp(LocationFact_TOMITA.type_1_TOMITA::not_norm) Word<kwtype="type_1"> | Word<kwtype="type_1"> Other2+ interp(LocationFact_TOMITA.type_1_TOMITA::not_norm);
Type_4_5 -> Other2+ interp(LocationFact_TOMITA.type_4_5_TOMITA::not_norm) Word<kwtype="type_4_5"> | Word<kwtype="type_4_5"> Other2+ interp(LocationFact_TOMITA.type_4_5_TOMITA::not_norm);
Type_3 -> Other2+ interp(LocationFact_TOMITA.type_3_TOMITA::not_norm) Word<kwtype="type_3"> | Word<kwtype="type_3"> Other2+ interp(LocationFact_TOMITA.type_3_TOMITA::not_norm);
Type_4 -> Other2+ interp(LocationFact_TOMITA.type_4_TOMITA::not_norm) Word<kwtype="type_4"> | Word<kwtype="type_4"> Other2+ interp(LocationFact_TOMITA.type_4_TOMITA::not_norm);
Type_2 -> Other2+ interp(LocationFact_TOMITA.type_2_TOMITA::not_norm) Word<kwtype="type_2"> | Word<kwtype="type_2"> Other2+ interp(LocationFact_TOMITA.type_2_TOMITA::not_norm);
Type_1_2 -> Other2+ interp(LocationFact_TOMITA.type_1_2_TOMITA::not_norm) Word<kwtype="type_1_2"> | Word<kwtype="type_1_2"> Other2+ interp(LocationFact_TOMITA.type_1_2_TOMITA::not_norm);
All -> Type_3_4 | Type_3_4_5 | Type_1_3_4 | Type_5 | Type_1 | Type_4_5 | Type_3 | Type_4 | Type_2 | Type_1_2 ;

Loc -> Loc1<~l-quoted, ~r-quoted> | Loc2<~l-quoted, ~r-quoted> | Loc3<~l-quoted, ~r-quoted> | Loc4<~l-quoted, ~r-quoted> | Loc5<~l-quoted, ~r-quoted>;

//Adr
Str -> Word<kwtype='street'> Punct* Word<h-reg1>+ interp(LocationFact_TOMITA.Str_TOMITA::not_norm) | Word<h-reg1>+ interp(LocationFact_TOMITA.Str_TOMITA::not_norm) Word<kwtype='street'> Punct*;

Allw -> All {weight = 0.9};
City -> Loc6 {weight = 0.5};
Locw -> Loc {weight = 0.7};

Location -> Locw interp(LocationFact_TOMITA.Location_TOMITA::not_norm) | Allw | Str | City interp(LocationFact_TOMITA.City_TOMITA::not_norm);