#encoding "utf-8"

Pers -> Word<kwtype="FIO">;

Wrong -> Word<kwset=~['street', 'location_front', 'location_back', "FIO"]>;

Pers0 -> Pers interp(PersonFact_TOMITA.Person_TOMITA::not_norm) Wrong;
Pers1 -> Pers<fw> interp(PersonFact_TOMITA.Person_TOMITA::not_norm) Punct;
Pers2 -> Pers<fw> interp(PersonFact_TOMITA.Person_TOMITA::not_norm) Wrong;
Pers3 -> Wrong Pers interp(PersonFact_TOMITA.Person_TOMITA::not_norm) Punct;
Pers4 -> Wrong Pers interp(PersonFact_TOMITA.Person_TOMITA::not_norm) Wrong;
Pers5 -> Pers2 Pers0* | Pers4 Pers0*;

Person -> Pers1 | Pers2 | Pers3 | Pers4 | Pers5;