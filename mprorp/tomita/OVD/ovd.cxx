#encoding "utf-8"
#GRAMMAR_ROOT Final

//Вспомогательные терминалы 
Other1 -> Prep | Word<gram="CONJ">;
Other2 -> Other1* Adj<h-reg1>+ | Other1 Noun<h-reg1, wfl=~'ОВД'>+;
Other3 -> Word Word{count = 5};
Q -> Word+;
Quote -> Q<quoted> interp(OVDFact_TOMITA.Name_TOMITA::not_norm);

//ОВД
ovd -> Word<kwtype="OVD"> interp(OVDFact_TOMITA.OVD_TOMITA::not_norm) Word<kwtype="RUS">*;
OVD -> ovd Quote* | ovd '№' AnyWord<wfl="[0-9]+"> interp(OVDFact_TOMITA.Numb_TOMITA::not_norm);
OVD_Q -> ovd Quote;

//Район/Регион/Город
Type_3_4 -> Other2+ interp(OVDFact_TOMITA.type_3_4_TOMITA::not_norm) Word<kwtype="type_3_4"> | Word<kwtype="type_3_4"> Other2+ interp(OVDFact_TOMITA.type_3_4_TOMITA::not_norm);
Type_3_4_5 -> Other2+ interp(OVDFact_TOMITA.type_3_4_5_TOMITA::not_norm) Word<kwtype="type_3_4_5"> | Word<kwtype="type_3_4_5"> Other2+ interp(OVDFact_TOMITA.type_3_4_5_TOMITA::not_norm);
Type_1_3_4 -> Other2+ interp(OVDFact_TOMITA.type_1_3_4_TOMITA::not_norm) Word<kwtype="type_1_3_4"> | Word<kwtype="type_1_3_4"> Other2+ interp(OVDFact_TOMITA.type_1_3_4_TOMITA::not_norm);
Type_5 -> Other2+ interp(OVDFact_TOMITA.type_5_TOMITA::not_norm) Word<kwtype="type_5"> | Word<kwtype="type_5"> Other2+ interp(OVDFact_TOMITA.type_5_TOMITA::not_norm); 
Type_1 -> Other2+ interp(OVDFact_TOMITA.type_1_TOMITA::not_norm) Word<kwtype="type_1"> | Word<kwtype="type_1"> Other2+ interp(OVDFact_TOMITA.type_1_TOMITA::not_norm);
Type_4_5 -> Other2+ interp(OVDFact_TOMITA.type_4_5_TOMITA::not_norm) Word<kwtype="type_4_5"> | Word<kwtype="type_4_5"> Other2+ interp(OVDFact_TOMITA.type_4_5_TOMITA::not_norm); 
Type_3 -> Other2+ interp(OVDFact_TOMITA.type_3_TOMITA::not_norm) Word<kwtype="type_3"> | Word<kwtype="type_3"> Other2+ interp(OVDFact_TOMITA.type_3_TOMITA::not_norm); 
Type_4 -> Other2+ interp(OVDFact_TOMITA.type_4_TOMITA::not_norm) Word<kwtype="type_4"> | Word<kwtype="type_4"> Other2+ interp(OVDFact_TOMITA.type_4_TOMITA::not_norm); 
Type_2 -> Other2+ interp(OVDFact_TOMITA.type_2_TOMITA::not_norm) Word<kwtype="type_2"> | Word<kwtype="type_2"> Other2+ interp(OVDFact_TOMITA.type_2_TOMITA::not_norm); 
Type_1_2 -> Other2+ interp(OVDFact_TOMITA.type_1_2_TOMITA::not_norm) Word<kwtype="type_1_2"> | Word<kwtype="type_1_2"> Other2+ interp(OVDFact_TOMITA.type_1_2_TOMITA::not_norm);
All -> Type_3_4 | Type_3_4_5 | Type_1_3_4 | Type_5 | Type_1 | Type_4_5 | Type_3 | Type_4 | Type_2 | Type_1_2 ;
Dis_OVD -> OVD All+;

//Локация 1
Locc -> Adj<h-reg1> | UnknownPOS<h-reg1>;
Loc_OVD -> Locc interp(OVDFact_TOMITA.Location_TOMITA::not_norm) OVD;

OVD_Q1 -> OVD_Q {weight = 0.9};
Dis_OVD1 -> Dis_OVD {weight = 0.5};
Loc_OVD1 -> Loc_OVD {weight = 0.9};
OVD1 -> OVD {weight = 0.2};

//Основное правило
Final -> Loc_OVD1 | Dis_OVD1 | OVD1 | OVD_Q1; 