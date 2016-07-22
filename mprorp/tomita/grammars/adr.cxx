#encoding "utf-8"

//Улица
Str -> Word<kwtype='street'> Punct* Word<h-reg1>+ | Word<h-reg1>+ Word<kwtype='street'> Punct*;
// Номер
Numb -> AnyWord<wfl="([0-9]+.*)*">;
// Дом
H -> Word<kwtype='house'> Punct* Numb | Numb | Numb '/' Numb;
// Квартира
Aprt -> Word<kwtype='apartment'> Punct* Word<wfl="[0-9]*"> | Word<wfl="[0-9]*">;

Adr1 -> Str Comma* H* Comma* Aprt*; 
Adr2 -> Aprt* Comma* H* Comma* Str;
Adr_A -> Adr1 | Adr2; 

Adr -> Adr_A interp(AdrFact_TOMITA.Adr_TOMITA::not_norm);
