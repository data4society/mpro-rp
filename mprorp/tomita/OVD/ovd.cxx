#encoding "utf-8"
#GRAMMAR_ROOT Final

//Вспомогательные терминалы 
Q -> Word+;
Quote -> Q<quoted> interp(OVDFact_TOMITA.Name_TOMITA::not_norm);

//ОВД
ovd -> Word<kwtype="OVD"> interp(OVDFact_TOMITA.OVD_TOMITA::not_norm) Word<kwtype="RUS">*;
OVD -> ovd Quote* | ovd '№' AnyWord<wfl="[0-9]+"> interp(OVDFact_TOMITA.Numb_TOMITA::not_norm);
OVD_Q -> ovd Quote;

//Локация 1
Locc -> Adj<h-reg1> | UnknownPOS<h-reg1>;
Loc_OVD -> Locc interp(OVDFact_TOMITA.Location_TOMITA::not_norm) OVD;

OVD_Q1 -> OVD_Q {weight = 0.9};
OVD1 -> OVD {weight = 0.2};

//Основное правило
Final -> OVD1 | OVD_Q1 | Loc_OVD;