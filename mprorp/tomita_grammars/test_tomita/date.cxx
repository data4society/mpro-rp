#encoding "utf-8"

Date1 -> AnyWord<wfl="[0-9]{1,2}"> Word<kwtype='month'>;
Date2 -> Word<kwtype="DATE">;
Date3 -> Date1 AnyWord<wfl="[0-9]{4}">;
Date4 -> Word<kwtype='week'>;

DateAll -> Date1 | Date2 | Date3 | Date4;
Date -> DateAll interp(DateFact_TOMITA.Date_TOMITA::not_norm);