#encoding "utf-8"

Person -> Word<kwset=["FIO"]> interp(PersonFact_TOMITA.Person_TOMITA::not_norm);
Pers -> Person<kwset=~["wrong_pers"]>;

Wrong -> AnyWord<kwset=~['street', 'location_front', 'location_back']>;

Pers0 -> Pers  Wrong | Pers  Punct;
Pers00 -> Wrong Pers;
Pers1 -> Pers<fw> Punct;
Pers2 -> Pers<fw> Wrong;
Pers3 -> Wrong Pers Punct;
Pers4 -> Wrong Pers Wrong;
Pers5 -> Pers2 Pers0* | Pers4 Pers0* | Pers00 Pers0*;

Persona -> Pers1 | Pers2 | Pers3 | Pers4 | Pers5;