#encoding "utf-8"

RF -> Word<kwtype='RF'>;
UK -> Word<kwtype='uk'> Word<h-reg1> | Word<kwtype='uk'> RF;

Connect -> SimConjAnd | Comma | ';';

St -> 'статья' | 'ст';
Art1 -> St AnyWord<wfl="[0-9]+"> Connect* | St '№' AnyWord<wfl="[0-9]+"> Connect*;
Art2 -> AnyWord<wfl="ст.?[0-9]+"> Connect*;
Art -> Art1 | Art2;

Ch -> 'часть' | 'ч';
Part1 -> Ch AnyWord<wfl="[0-9]+"> Connect* | Ch '№' AnyWord<wfl="[0-9]+"> Connect*;
Part2 -> AnyWord<wfl="ч.?[0-9]+"> Connect*;
Part -> Part1 | Part2;

Pun -> 'пункт' | 'п';
P1 -> AnyWord<wfl="([а-я]|[А-Я])"> Connect*;
P2 -> AnyWord<wfl="[0-9]+"> Connect;
Point -> Pun P2+ | Pun '№' P2+ | Pun P1+ |Pun '№' P1+;

Act1 -> Point+ interp(NormFact_TOMITA.Norm_TOMITA::not_norm);
Act2 -> Part+ interp(NormFact_TOMITA.Norm_TOMITA::not_norm);
Act3 -> Art+ interp(NormFact_TOMITA.Norm_TOMITA::not_norm);
Act4 -> UK interp(NormFact_TOMITA.Norm_TOMITA::not_norm);
Act -> Act1 | Act2 | Act3 | Act4;
