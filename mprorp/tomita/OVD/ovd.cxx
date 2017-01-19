#encoding "utf-8"
#GRAMMAR_ROOT Final

//Вспомогательные терминалы 
Q -> Word+;
Quote -> Q<quoted> interp(OVDFact_TOMITA.Name_TOMITA::not_norm);

//ОВД
ovd -> Word<kwtype="OVD2"> interp(OVDFact_TOMITA.OVD_TOMITA::not_norm) Word<kwtype="RUS">*;
OVD_N -> ovd '№' AnyWord<wfl="[0-9]+"> interp(OVDFact_TOMITA.Numb_TOMITA::not_norm) | AnyWord<wfl="[0-9]+"> interp(OVDFact_TOMITA.Numb_TOMITA::not_norm) ovd | OrdinalNumeral interp(OVDFact_TOMITA.Numb_TOMITA::not_norm) ovd;
OVD_Q -> ovd Quote | OVD_N Quote;

//Локация 1
//Locc -> Adj<h-reg1> | UnknownPOS<h-reg1>;
//Loc_OVD -> Locc interp(OVDFact_TOMITA.Location_TOMITA::not_norm) ovd | Locc interp(OVDFact_TOMITA.Location_TOMITA::not_norm) OVD_N;

OVD_Q1 -> OVD_Q {weight = 0.9};
//OVD_Loc1 -> Loc_OVD {weight = 0.2};
OVD_N1 -> OVD_N {weight = 0.3};
OVD1 -> ovd {weight = 0.1};

//Основное правило
Final -> OVD1 | OVD_Q1 | OVD_N1; //OVD_Loc1