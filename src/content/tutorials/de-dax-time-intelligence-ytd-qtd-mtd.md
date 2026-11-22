---
title: "YTD, QTD und MTD in DAX: Zeitintelligenz richtig aufsetzen"
description: "TOTALYTD, DATEADD und SAMEPERIODLASTYEAR liefern nur mit einer markierten Kalendertabelle verlässliche Werte. Aufbau, Syntax und fünf Fehler, die YTD stillschweigend verfälschen."
pubDate: 2026-11-22
updatedDate: 2026-11-22
category: "time-intelligence"
difficulty: "Intermediate"
tags: ["zeitintelligenz", "dax", "ytd", "dateadd", "kalendertabelle"]
author: Mireia
featured: false
draft: false
---

Umsatz seit Jahresbeginn, Quartalszahlen und der Vergleich mit dem Vorjahr gehören zum Tagesgeschäft jedes Controllings. Genau diese Kennzahlen sind aber auch die DAX-Berechnungen, die am häufigsten stillschweigend falsche Werte liefern — nicht weil die Funktionen kompliziert wären, sondern weil die Voraussetzung fehlt: eine saubere, als Datumstabelle markierte Kalendertabelle. Microsoft beschreibt die Grundlagen dazu in der [Referenz zur DATE-Funktion](https://learn.microsoft.com/de-de/dax/date-function-dax).

Diese Anleitung zeigt die fünf wichtigsten Zeitintelligenz-Funktionen, die Anforderungen an die Kalendertabelle und die fünf Fehler, die zu falschen Zahlen führen, ohne eine Fehlermeldung zu erzeugen.

## Die Voraussetzung: eine echte Kalendertabelle

Jede Zeitintelligenz-Funktion in DAX hat eine nicht verhandelbare Bedingung: **eine als Datumstabelle markierte Tabelle mit lückenlos aufeinanderfolgenden Datumswerten**. Fehlt sie, liefern YTD-Berechnungen leere, falsche oder je nach Filterkontext wechselnde Ergebnisse.

### Was „markiert“ bedeutet

In Power BI Desktop wählen Sie die Kalendertabelle aus, öffnen **Tabellentools → Als Datumstabelle markieren** und bestimmen die Datumsspalte. Damit weiß das Modell, dass es sich um eine echte Datumsspalte handelt, und schaltet die Zeitintelligenz-Funktionen frei. In der Modellansicht lässt sich dieselbe Einstellung über die Eigenschaften der Tabelle setzen.

### Wie eine saubere Kalendertabelle aussieht

Die folgende berechnete Tabelle erzeugt einen durchgehenden Kalender vom 01.01.2020 bis 31.12.2026 und ergänzt die Attribute, die ein Bericht typischerweise braucht:

```dax
Kalender =
VAR StartDatum = DATE(2020, 1, 1)
VAR EndDatum = DATE(2026, 12, 31)
VAR Tage =
    SELECTCOLUMNS(
        CALENDAR(StartDatum, EndDatum),
        "Datum", [Date]
    )
RETURN
    ADDCOLUMNS(
        Tage,
        "Jahr", YEAR([Datum]),
        "Quartal", "Q" & FORMAT([Datum], "Q"),
        "Quartalsnummer", FORMAT([Datum], "Q"),
        "Monat", FORMAT([Datum], "MM"),
        "Monatsname", FORMAT([Datum], "MMMM"),
        "MonatsKurz", FORMAT([Datum], "MMM"),
        "Wochentag", FORMAT([Datum], "dddd"),
        "WochentagNr", WEEKDAY([Datum], 2),
        "Arbeitstag", WEEKDAY([Datum], 2) <= 5,
        "Geschäftsjahr",
            VAR M = MONTH([Datum])
            RETURN IF(M >= 7, YEAR([Datum]) + 1, YEAR([Datum])),
        "Geschäftsquartal",
            VAR M = MONTH([Datum])
            RETURN "Q" & FORMAT(IF(M >= 7, M - 6, M + 6), "0")
    )
```

**Die vier Pflichten einer Kalendertabelle**:

- Die Datumsspalte hat den Typ `Datum` — nicht Text und nicht Datum/Uhrzeit.
- Der Bereich ist **lückenlos**; kein Tag fehlt.
- Die Tabelle ist **als Datumstabelle markiert**.
- Eine **Beziehung** verbindet sie mit den Faktentabellen.

Fehlt einer dieser Punkte, rechnen die Funktionen ohne Fehlermeldung weiter — und liefern BLANK oder Werte, die nur zufällig stimmen.

> **Sortierung nicht vergessen:** `Monatsname` und `MonatsKurz` werden alphabetisch sortiert, sobald sie in einem Visual liegen. Ordnen Sie diese Spalten über **Nach Spalte sortieren** der Spalte `Monat` zu, damit Januar vor Februar steht und nicht April vor August.

## Die fünf Kernfunktionen

### Funktion 1: TOTALYTD (Jahr bis heute)

**Szenario**: Der kumulierte Umsatz vom 01.01. bis zum aktuellen Datum.

```dax
Umsatz YTD =
TOTALYTD(
    [Umsatz],
    'Kalender'[Datum]
)
```

**So funktioniert es**: `TOTALYTD` wertet `[Umsatz]` für alle Datumswerte vom Jahresanfang bis zum **spätesten Datum im aktuellen Filterkontext** aus. Zeigt das Visual den März 2024, liefert das Measure die Summe aus Januar, Februar und März 2024.

**Mit Geschäftsjahr** (beispielsweise Juli bis Juni):

```dax
Umsatz GJ YTD =
TOTALYTD(
    [Umsatz],
    'Kalender'[Datum],
    "30.06."
)
```

Das dritte Argument teilt `TOTALYTD` mit, dass das Geschäftsjahr am 30.06. endet; die Kumulierung beginnt folglich am 01.07. neu. Das Format richtet sich nach dem Gebietsschema des Modells — in einem englischsprachigen Modell schreiben Sie stattdessen `"06-30"`.

### Funktion 2: TOTALQTD (Quartal bis heute)

```dax
Umsatz QTD =
TOTALQTD(
    [Umsatz],
    'Kalender'[Datum]
)
```

Das Measure summiert den Umsatz vom ersten Tag des aktuellen Quartals bis zum spätesten Datum im Filterkontext. Zeigt das Visual den Mai 2024, enthält das Ergebnis April und Mai 2024.

### Funktion 3: TOTALMTD (Monat bis heute)

```dax
Umsatz MTD =
TOTALMTD(
    [Umsatz],
    'Kalender'[Datum]
)
```

Hier beginnt die Summierung am ersten Tag des laufenden Monats. Steht der Filter auf dem 15.03.2024, rechnet `TOTALMTD` den Zeitraum 01.03. bis 15.03.2024.

### Funktion 4: DATEADD (Zeitraumvergleich)

**Szenario**: Der Umsatz des laufenden Zeitraums soll dem gleichen Zeitraum des Vorjahres gegenübergestellt werden.

```dax
Umsatz Vorjahr =
CALCULATE(
    [Umsatz],
    DATEADD('Kalender'[Datum], -1, YEAR)
)
```

`DATEADD` verschiebt den Datumsfilter um eine bestimmte Anzahl von Intervallen. `-1, YEAR` bedeutet „gleicher Zeitraum, ein Jahr früher“. Steht der Filter auf März 2024, liest das Measure den März 2023.

**Weitere Intervalle**:

```dax
-- Gleicher Zeitraum, ein Quartal früher
Umsatz Vorquartal =
CALCULATE([Umsatz], DATEADD('Kalender'[Datum], -1, QUARTER))

-- Gleicher Zeitraum, einen Monat früher
Umsatz Vormonat =
CALCULATE([Umsatz], DATEADD('Kalender'[Datum], -1, MONTH))
```

### Funktion 5: SAMEPERIODLASTYEAR (die Kurzform)

```dax
Umsatz Vorjahreszeitraum =
CALCULATE(
    [Umsatz],
    SAMEPERIODLASTYEAR('Kalender'[Datum])
)
```

Die Funktion entspricht `DATEADD('Kalender'[Datum], -1, YEAR)`, ist aber lesbarer. Verwenden Sie sie, wenn die Absicht ausdrücklich „gleicher Zeitraum, ein Jahr zurück“ lautet.

## Umsatzwachstum berechnen (das Praxismuster)

Aus diesen Bausteinen entsteht die wohl häufigste Zeitintelligenz-Kennzahl: das Wachstum gegenüber dem Vorjahr.

```dax
Umsatzwachstum % =
VAR AktuellerUmsatz = [Umsatz]
VAR Vorjahresumsatz =
    CALCULATE(
        [Umsatz],
        SAMEPERIODLASTYEAR('Kalender'[Datum])
    )
RETURN
    DIVIDE(
        AktuellerUmsatz - Vorjahresumsatz,
        Vorjahresumsatz
    )
```

**Warum hier Variablen stehen**: `Vorjahresumsatz` hält den Wert fest, bevor weitere Filteränderungen greifen; `AktuellerUmsatz` ebenso. Beide sind Momentaufnahmen. Würden Sie die Ausdrücke direkt in `DIVIDE` einsetzen, würde DAX sie mehrfach auswerten — langsamer und schwerer zu debuggen.

Ein durchgerechnetes Beispiel: Die fiktive Nordlicht Handel GmbH erwirtschaftet von Januar bis September 2026 einen Umsatz von 1.240.000 €, im gleichen Zeitraum 2025 waren es 1.080.000 €. Das Measure liefert 14,8 Prozent Wachstum. Wichtig ist, dass beide Werte aus demselben Filterkontext stammen — sonst vergleichen Sie Äpfel mit Birnen.

## Die fünf Fehler, die falsche Zahlen erzeugen

### Fehler 1: Keine markierte Datumstabelle

**Das Problem**: `TOTALYTD([Umsatz], 'Kalender'[Datum])` liefert BLANK oder exakt denselben Wert wie `[Umsatz]`.

**Die Ursache**: Die Kalendertabelle ist nicht als Datumstabelle markiert. Ohne diese Markierung kann die Engine die Jahresgrenzen nicht bestimmen.

**Die Lösung**: Tabelle auswählen → **Tabellentools → Als Datumstabelle markieren** → Datumsspalte wählen. Prüfen Sie zusätzlich unter **Datei → Optionen und Einstellungen → Optionen → Daten laden**, ob **Automatisches Datum/Uhrzeit** deaktiviert ist. Die automatisch erzeugten Datumstabellen konkurrieren sonst mit Ihrer eigenen.

### Fehler 2: Lücken im Datumsbereich

**Das Problem**: Die YTD-Berechnung springt mitten im Jahr zurück oder liefert für einzelne Monate unerwartete Werte.

**Die Ursache**: Der Kalendertabelle fehlen Tage, an denen es keine Verkäufe gab. Das passiert typischerweise, wenn die Tabelle mit `DISTINCT(Sales[OrderDate])` statt mit `CALENDAR()` aufgebaut wird.

```dax
-- FALSCH: erzeugt Lücken an verkaufsfreien Tagen
Kalender = DISTINCT(Vertrieb[Bestelldatum])

-- RICHTIG: lückenloser Datumsbereich
Kalender = CALENDAR(DATE(2020, 1, 1), DATE(2026, 12, 31))
```

Zeitintelligenz-Funktionen gehen davon aus, dass jeder Tag des Zeitraums existiert. Fehlt der 15.05., endet `TOTALYTD` möglicherweise bereits am 14.05.

### Fehler 3: DATEADD ohne Verständnis der Granularität

**Das Problem**: Der Vorjahresvergleich stimmt auf Monatsebene, liefert auf Tages- oder Quartalsebene aber falsche Werte.

**Die Ursache**: `DATEADD` verschiebt den **Filterkontext** auf der Datumsspalte. Zeigt das Visual Monate, verschiebt `-1, YEAR` den gesamten Monatsfilter. Zeigt es Tage, wird der Tagesfilter verschoben. Die Funktion arbeitet auf der Granularität, die der Filterkontext vorgibt.

```dax
-- Visual zeigt März 2024 → Ergebnis: März 2023 (korrekt)
-- Visual zeigt 15.03.2024 → Ergebnis: 15.03.2023 (korrekt)
-- Visual zeigt Q1 2024 → Ergebnis: Q1 2023 (korrekt)
Umsatz Vorjahr = CALCULATE([Umsatz], DATEADD('Kalender'[Datum], -1, YEAR))
```

Die Funktion rechnet auf jeder Granularität richtig — entscheidend ist, dass die Granularität vom **Visual** bestimmt wird und nicht vom DAX-Code.

### Fehler 4: TOTALYTD ignoriert den Filterkontext nicht

**Das Problem**: Das YTD-Measure zeigt den gesamten Jahresumsatz statt des Umsatzes bis heute.

**Die Ursache**: `TOTALYTD` summiert vom 01.01. bis zum **spätesten Datum im Filterkontext**. Enthält das Visual oder der Datenschnitt das ganze Jahr — etwa `Jahr = 2024` ohne Monatsfilter —, ist das Ergebnis zwangsläufig der Jahresumsatz.

**Die Lösung**: Sorgen Sie dafür, dass der Filterkontext den gewünschten Monat oder Tag enthält. Zeigt das Visual einen konkreten Monat, kumuliert `TOTALYTD` korrekt bis zu diesem Monat.

```dax
-- Visual zeigt März 2024 → YTD = Januar + Februar + März 2024 (korrekt)
-- Visual zeigt 2024 (ganzes Jahr) → YTD = gesamtes Jahr 2024
--   (rechnerisch ebenfalls korrekt, aber nicht die gewünschte Aussage)
Umsatz YTD = TOTALYTD([Umsatz], 'Kalender'[Datum])
```

### Fehler 5: Kalenderarten vermischen

**Das Problem**: Das Geschäftsjahres-YTD springt im Januar statt im Juli zurück, oder das normale YTD enthält die Grenztage des Geschäftsjahres falsch.

**Die Ursache**: Sie verwenden die Standardfunktion `TOTALYTD` ohne Parameter für das Geschäftsjahresende, obwohl Ihr Unternehmen nach einem abweichenden Kalender wirtschaftet.

```dax
-- FALSCH: nutzt das Kalenderjahr (Januar–Dezember) statt des Geschäftsjahres (Juli–Juni)
Umsatz YTD falsch = TOTALYTD([Umsatz], 'Kalender'[Datum])

-- RICHTIG: Geschäftsjahr endet am 30.06.
Umsatz GJ YTD = TOTALYTD([Umsatz], 'Kalender'[Datum], "30.06.")
```

Das dritte Argument erwartet einen String im Format des Modell-Gebietsschemas, der den letzten Tag des Geschäftsjahres bezeichnet. Übliche Werte:

- `"31.12."` — Kalenderjahr (Standard)
- `"30.06."` — Geschäftsjahr Juli–Juni
- `"31.03."` — Geschäftsjahr April–März (unter anderem in Großbritannien und Japan)
- `"30.09."` — Geschäftsjahr Oktober–September (US-Bundesbehörden)

## Entscheidungshilfe: welche Funktion wann?

| Anforderung | Funktion | Beispiel |
|---|---|---|
| Kumuliert ab Jahresbeginn | `TOTALYTD` | Umsatz YTD bis zum aktuellen Monat |
| Kumuliert ab Quartalsbeginn | `TOTALQTD` | Umsatz QTD bis zum aktuellen Monat |
| Kumuliert ab Monatsbeginn | `TOTALMTD` | Umsatz MTD bis zum aktuellen Tag |
| Vergleich mit Vorperiode (beliebiges Intervall) | `DATEADD` | Gleicher Monat oder gleiches Quartal im Vorjahr |
| Vergleich mit dem Vorjahreszeitraum (Kurzform) | `SAMEPERIODLASTYEAR` | Gleicher Monat, gleiches Quartal, gleiches Jahr |
| Vergleich mit einem frei verschobenen Zeitraum | `DATEADD` mit eigenem Offset | Vor drei Monaten, vor zwei Quartalen |
| Rollierende zwölf Monate | eigenes Muster mit `DATESINPERIOD` | Umsatz der letzten zwölf Monate |

### Rollierende zwölf Monate (fortgeschrittenes Muster)

```dax
Umsatz letzte 12 Monate =
CALCULATE(
    [Umsatz],
    DATESINPERIOD(
        'Kalender'[Datum],
        MAX('Kalender'[Datum]),
        -12,
        MONTH
    )
)
```

`DATESINPERIOD` liefert eine Tabelle mit allen Datumswerten der letzten zwölf Monate, gerechnet ab dem spätesten Datum im aktuellen Filterkontext. Das Muster eignet sich für gleitende Durchschnitte und für den Vergleich mit dem gesamten Vorjahreszeitraum.

## Häufige Fragen

**F: Muss ich Automatisches Datum/Uhrzeit deaktivieren?**

Ja. Die Option erzeugt für jede Datumsspalte im Modell eine versteckte Datumstabelle. Das vergrößert das Modell und kollidiert mit Ihrer eigenen Kalendertabelle. Unter **Datei → Optionen und Einstellungen → Optionen → Daten laden** lässt sich die Funktion für die aktuelle Datei abschalten.

**F: Was passiert mit Fakten, deren Datum außerhalb der Kalendertabelle liegt?**

Diese Zeilen fließen nicht in Zeitintelligenz-Berechnungen ein, weil die Beziehung nur Datumswerte umfasst, die in der Kalendertabelle vorhanden sind. Erweitern Sie den Kalenderbereich so, dass er alle Datumswerte der Faktentabelle abdeckt.

**F: Funktioniert Zeitintelligenz auch mit DirectQuery?**

Ja, aber die Abfragen können deutlich langsamer sein. Zeitintelligenz-Funktionen erzeugen im Hintergrund komplexe SQL-Abfragen. Bei DirectQuery-Modellen ist es oft sinnvoller, YTD-, QTD- und MTD-Werte bereits in der Quelle zu berechnen — etwa in einer SQL-Sicht — und als Spalten zu importieren.

**F: Worin unterscheiden sich DATESYTD und TOTALYTD?**

`TOTALYTD` ist eine Kurzform aus `CALCULATE` und `DATESYTD`. Die beiden Measures sind gleichwertig:

```dax
-- Mit TOTALYTD (empfohlen, weil kürzer)
Umsatz YTD = TOTALYTD([Umsatz], 'Kalender'[Datum])

-- Mit CALCULATE und DATESYTD (explizit)
Umsatz YTD = CALCULATE([Umsatz], DATESYTD('Kalender'[Datum]))
```

Nehmen Sie `TOTALYTD` für Lesbarkeit. `DATESYTD` bietet sich an, wenn Sie die Datumstabelle selbst weiterverarbeiten wollen, beispielsweise in einem komplexeren `CALCULATE` mit zusätzlichen Filtern.

**F: Wie behandle ich 4-4-5-Geschäftskalender?**

Die Standardfunktionen gehen von Kalendermonaten aus. Für 4-4-5-Kalender, wie sie im Einzelhandel verbreitet sind, brauchen Sie eigene DAX-Muster. Legen Sie eine Spalte `Geschäftsperiode` in der Kalendertabelle an und berechnen Sie die kumulierten Werte anhand der Periodennummer statt anhand des Kalenderdatums.

## Wie es weitergeht

Zeitintelligenz baut auf den DAX-Grundlagen auf und lässt sich gut mit diesen Themen vertiefen:

- [DAX Grundlagen](/tutorials/de-dax-basics/) — Measures, Filterkontext und die ersten Formeln, auf denen jede Zeitintelligenz-Berechnung steht.
- [SWITCH in DAX](/tutorials/de-dax-switch-function/) — damit Anwender per Datenschnitt zwischen YTD, QTD und MTD umschalten können.
- [DAX Time Intelligence: YTD, QTD, and MTD Complete Guide](/tutorials/dax-time-intelligence-ytd-qtd-mtd/) — die englische Originalfassung dieses Artikels.
