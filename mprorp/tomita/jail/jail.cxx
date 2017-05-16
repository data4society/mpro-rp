#encoding "utf-8"

//Jail
Jail1 -> Word<kwtype='Jail1'> interp(JailFact_TOMITA.Jail_TOMITA::not_norm);
Jail2 -> Word<kwtype='Jail2'> interp(JailFact_TOMITA.Jail_TOMITA::not_norm);
Jail3 -> Word<h-reg1, kwtype='Jail3'> interp(JailFact_TOMITA.Jail_TOMITA::not_norm);
Jail -> Jail1 | Jail2 | Jail3;