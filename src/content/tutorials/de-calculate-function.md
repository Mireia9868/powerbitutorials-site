---
title: "CALCULATE in DAX: Filterkontext verstehen und gezielt ändern"
description: "CALCULATE ist die einzige DAX-Funktion, die den Filterkontext ändert. Auswertungsreihenfolge, drei Muster und die typischen Fehler verständlich erklärt."
pubDate: 2026-11-24
updatedDate: 2026-11-24
category: "dax"
difficulty: "Intermediate"
tags: ["dax", "calculate", "filterkontext", "dax-funktionen", "fortgeschritten"]
author: Mireia
featured: false
draft: false
---

`CALCULATE` ist in DAX die Funktion, die den Filterkontext ändert. Wenn DAX eine Chef-Funktion hat, dann diese: Jedes fortgeschrittene Muster — Zeitintelligenz, Anteil am Gesamtwert, Kohortenanalyse, gleitende Durchschnitte — hängt daran.

Diese Anleitung erklärt, warum `CALCULATE` eine Sonderstellung hat, wie Sie die Funktion richtig einsetzen und welche Verhaltensweisen für die meisten DAX-Fehler auf mittlerem Niveau verantwortlich sind. Die Beispiele stammen aus dem Vertriebsmodell der Nordlicht Gerätebau GmbH in Kiel, einem Messgerätehersteller mit 48 Mio. € Jahresumsatz.

> **Verwendetes Modell.** Die Formeln gehen von einer Tabelle `Vertrieb` mit den Spalten `Vertrieb[Menge]`, `Vertrieb[Einzelpreis]`, `Vertrieb[Einzelkosten]`, `Vertrieb[Rabatt]` und `Vertrieb[Umsatz]` aus. Dazu kommt eine Tabelle `Datum`, die bereits als Datumstabelle markiert und mit `Vertrieb` verknüpft ist. Jedes Codeschnipsel läuft in dieser Konstellation unverändert.

## Warum CALCULATE den Unterschied macht

DAX-Measures werden in einem **Filterkontext** ausgewertet — der Menge der Zeilen, die aufgrund von Datenschnitten, Visual-Interaktionen und Modellbeziehungen sichtbar sind. In den meisten Fällen ist das genau richtig. Manchmal müssen Sie diesen Kontext aber *überschreiben* oder *erweitern*:

- Den Gesamtumsatz des Unternehmens neben dem Umsatz jeder Region zeigen (Regionalfilter ignorieren)
- Denselben Zeitraum im Vorjahr berechnen (Datumsfilter um zwölf Monate zurückverschieben)
- Einen Quotienten gegen einen Nenner bilden, der einen bestimmten Filter ignorieren soll
- Eine Bedingung abhängig von der Auswahl im Datenschnitt anwenden

`CALCULATE` ist die **einzige** Funktion in DAX, die den Filterkontext verändern kann. Alles andere — `ALL`, `FILTER`, die Zeitintelligenz-Funktionen — wirkt nur, *weil* es an `CALCULATE` übergeben wird.

Wer schon einmal vor einem Measure gesessen hat und sich gefragt hat, warum in jeder Zeile einer Matrix dieselbe Zahl steht oder warum der Prozentwert immer 100 ergibt: Die Antwort ist fast immer, dass `CALCULATE` fehlt, um den Filterkontext im Nenner anzupassen.

## Syntax und Auswertungsreihenfolge

```dax
CALCULATE(
    <Ausdruck>,
    <Filter1>,
    <Filter2>,
    ...
)
```

- `Ausdruck` — die DAX-Formel, die ausgewertet wird, meist ein Measure oder eine Aggregation.
- `FilterN` — optionale Filterargumente, die den Kontext ändern, bevor der Ausdruck läuft.

Die drei Modifikatoren, die das Verhalten dieser Filter steuern — `KEEPFILTERS`, `REMOVEFILTERS` und `ALLSELECTED` — lassen sich leicht verwechseln. Die [DAX-Funktionsreferenz](/tools/dax-functions/) listet sie mit exakter Syntax, sodass Sie die Argumentreihenfolge prüfen können, bevor Sie die Formel einfügen.

Entscheidend ist die Reihenfolge der Auswertung. Hier stolpern die meisten Einsteiger:

1. Der Filterkontext des Visuals wird übernommen.
2. Jedes Filterargument wird **im ursprünglichen Kontext** ausgewertet, nicht im bereits geänderten.
3. Die Filterargumente werden mit UND verknüpft.
4. Die Filter **ersetzen** bestehende Filter auf derselben Spalte oder **ergänzen** Filter auf neuen Spalten.
5. Der Ausdruck wird im neuen, geänderten Kontext ausgewertet.

Schritt 4 ist der Kern: `CALCULATE` addiert keine Filter, sondern **ersetzt** sie auf den Spalten, die Sie nennen. Filtert das Visual auf „Messgeräte" und Ihr `CALCULATE` setzt `Produkt[Kategorie] = "Zubehör"`, zeigt das Ergebnis den Umsatz von Zubehör — nicht die Summe beider Kategorien.

## Muster 1: Anteil am Gesamtumsatz

Der Klassiker — der Beitrag jeder Kategorie zum Gesamtergebnis:

```dax
// Gesamtumsatz: der Zähler folgt den Filtern
Gesamtumsatz = SUM(Vertrieb[Umsatz])

// Umsatz gesamt: der Nenner ignoriert den Kategoriefilter
Umsatz Gesamt =
CALCULATE(
    [Gesamtumsatz],
    ALL(Produkt[Kategorie])
)

// Anteil in Prozent
Kategorie % vom Gesamt =
DIVIDE(
    [Gesamtumsatz],
    [Umsatz Gesamt]
)
```

`ALL(Produkt[Kategorie])` entfernt jeden Filter auf der Spalte `Kategorie`. Filtert das Visual auf „Messgeräte", liefert `[Umsatz Gesamt]` trotzdem den Wert über alle Kategorien — genau das, was der Nenner braucht. Für Sonderfälle lohnt ein Blick in die [ALL-Referenz](https://learn.microsoft.com/de-de/dax/all-function-dax).

> **Die richtige ALL-Variante wählen:**
> - `ALL(Tabelle[Spalte])` — entfernt den Filter auf einer Spalte
> - `ALL(Tabelle)` — entfernt alle Filter auf dieser Tabelle
> - `ALL()` ohne Argumente — entfernt alle Filter überall (mächtig, aber riskant)
> - `ALLSELECTED(Tabelle[Spalte])` — entfernt Filter innerhalb des Visuals, behält aber Datenschnitt-Filter (für „Anteil am sichtbaren Gesamt")
> - `REMOVEFILTERS()` — seit 2019 der sprechendere Alias für `ALL`. Für die Lesbarkeit meist die bessere Wahl.

### Variante: Anteil am Elternteil in einer Hierarchie

Gruppiert das Visual nach Kategorie → Unterkategorie → Produkt, ist oft nicht der Gesamtwert gefragt, sondern der Anteil an der Elternkategorie. Dafür ist `ALLSELECTED` zuständig:

```dax
% der Elternkategorie =
DIVIDE(
    [Gesamtumsatz],
    CALCULATE([Gesamtumsatz], ALLSELECTED(Produkt[Unterkategorie]))
)
```

Der Produktfilter fällt weg, der Kategoriefilter der Hierarchie bleibt erhalten. Das Ergebnis ist der Beitrag der Unterkategorie zu ihrer Kategorie.

## Muster 2: Vorjahresvergleich

```dax
Umsatz Vorjahr =
CALCULATE(
    [Gesamtumsatz],
    SAMEPERIODLASTYEAR(Datum[Datum])
)

Wachstum ggü. Vorjahr % =
DIVIDE(
    [Gesamtumsatz] - [Umsatz Vorjahr],
    [Umsatz Vorjahr]
)
```

`SAMEPERIODLASTYEAR` ist eine Zeitintelligenz-Funktion, die intern `CALCULATE` mit einem um ein Jahr verschobenen Datumsfilter aufruft. Alle Zeitintelligenz-Funktionen setzen eine korrekt **markierte Datumstabelle** voraus — die Einrichtung beschreibt die Anleitung zur [Zeitintelligenz in Power BI](/tutorials/de-dax-time-intelligence-ytd-qtd-mtd/).

**Häufiger Fehler:** Liefert `[Umsatz Vorjahr]` in allen Zeilen LEER, ist die Datumstabelle nicht markiert. In der Modellansicht die Tabelle auswählen, dann **Als Datumstabelle markieren** und die Datumsspalte wählen. Das ist die häufigste Ursache dafür, dass Zeitintelligenz-Measures stillschweigend scheitern.

Für den Vergleich mit dem Vorjahr gilt außerdem: Achten Sie auf ein vollständiges Datumsraster. Fehlt der 29.02. in einem Schaltjahr, verschiebt `SAMEPERIODLASTYEAR` den Zeitraum und der Vergleich stimmt um einen Tag nicht. Die Datumstabelle sollte deshalb lückenlos vom 01.01. des ersten bis zum 31.12. des letzten Geschäftsjahres reichen.

## Muster 3: Summe mit einer Bedingung

Alle Rechnungen summieren, aber nur die als bezahlt markierten — unabhängig von jedem anderen Filter im Visual:

```dax
Bezahlter Umsatz =
CALCULATE(
    [Gesamtumsatz],
    Vertrieb[Status] = "Bezahlt"
)
```

Boolesche Filter wie `Vertrieb[Status] = "Bezahlt"` sind die einfachste Form eines Filterarguments. Sie funktionieren für eine Spalte und einen Wert, alternativ mit einer `IN`-Liste. Für komplexere Logik braucht es `FILTER`:

```dax
Umsatz bezahlt ab 1.000 € =
CALCULATE(
    [Gesamtumsatz],
    FILTER(
        ALL(Vertrieb),
        Vertrieb[Status] = "Bezahlt" && Vertrieb[Umsatz] > 1000
    )
)
```

`FILTER` gibt eine gefilterte Tabelle zurück, die `CALCULATE` als Filterargument übernimmt. Wichtig ist das `ALL(Vertrieb)` innerhalb von `FILTER`: Die Bedingung wird über die gesamte Tabelle ausgewertet und ignoriert den Filterkontext des Visuals.

![Formelleiste in Power BI Desktop mit dem Measure Bezahlter Umsatz aus CALCULATE und dem Filter Status = Bezahlt](/images/tutorials/calculate-function/01-measure-formula-bar.png)

### Wann FILTER, wann boolescher Filter?

| Situation | Empfehlung |
|---|---|
| Eine Spalte, ein Wert | Boolesch: `Vertrieb[Status] = "Bezahlt"` |
| Eine Spalte, mehrere Werte | Boolesch: `Vertrieb[Status] IN {"Bezahlt", "Offen"}` |
| Bedingung über mehrere Spalten | `FILTER(Tabelle, Bed1 && Bed2)` |
| Bedingung, die ein Measure referenziert | `FILTER(VALUES(Tabelle[Spalte]), [Measure] > 100)` |
| Auswertung über die ganze Tabelle, Kontext ignorieren | `FILTER(ALL(Tabelle), ...)` |

**Hinweis zur Performance:** `FILTER(ALL(Vertrieb), ...)` liest jede Zeile der Faktentabelle. Bei 50 Millionen Zeilen ist das tödlich. Für einfache Spaltenfilter immer die boolesche Form verwenden — sie nutzt das Spaltenwörterbuch von VertiPaq und ist um Größenordnungen schneller.

## Der häufigste Denkfehler: Filter addieren sich nicht

Ein verbreiteter Irrtum ist, dass Filterargumente sich verketteten. Sie werden mit UND verknüpft, aber jedes einzelne arbeitet auf dem **ursprünglichen** Kontext:

```dax
// Das ist tatsächlich "Kategorie = Messgeräte UND Jahr = 2026".
// Beide Filter ersetzen bestehende Filter auf ihrer jeweiligen Spalte.
CALCULATE(
    [Gesamtumsatz],
    Produkt[Kategorie] = "Messgeräte",
    Datum[Jahr] = 2026
)
```

Dieses Beispiel verhält sich wie erwartet. Überraschend wird es mit `ALL`:

```dax
// Entfernt den Kategoriefilter und danach alle Datumsfilter.
// Zwei ALL-Aufrufe stapeln sich nicht — jeder entfernt den Filter seiner Spalte.
CALCULATE(
    [Gesamtumsatz],
    ALL(Produkt[Kategorie]),
    ALL(Datum)
)
```

Müssen Filter auf mehreren Tabellen in einem Schritt entfernt werden, hilft `ALL(Tabelle1, Tabelle2)` oder `REMOVEFILTERS(Tabelle1, Tabelle2)`.

## Kontextübergang: die unterschätzte Falle

Wird `CALCULATE` in einem Iterator (`SUMX`, `FILTER`, `ADDCOLUMNS`) verwendet, findet ein **Kontextübergang** statt: Der Zeilenkontext des Iterators wird in einen Filterkontext auf der aktuellen Zeile umgewandelt.

```dax
// Ohne CALCULATE — falsche Summen
Falsche Marge =
SUMX(
    Vertrieb,
    Vertrieb[Umsatz] - Vertrieb[Einzelkosten] * Vertrieb[Menge]
)

// Mit CALCULATE — der Kontextübergang macht RELATED() nutzbar
Richtige Marge =
SUMX(
    Vertrieb,
    CALCULATE(Vertrieb[Umsatz] - RELATED(Produkt[Herstellkosten]) * Vertrieb[Menge])
)
```

Das `CALCULATE` innerhalb von `SUMX` wandelt den Zeilenkontext in einen Filterkontext um. Erst dadurch kann `RELATED()` die Beziehung zur Produkttabelle nutzen. Ohne diesen Schritt schlägt `RELATED()` fehl, weil kein Filterkontext die Beziehung auflöst.

**Regel:** Wer innerhalb eines Iterators Spalten aus verknüpften Tabellen referenziert, packt den Ausdruck in `CALCULATE`. Das ist die häufigste Ursache für „die Summen stimmen nicht, die Zeilenwerte sehen aber richtig aus".

## CALCULATE gegen CALCULATETABLE

`CALCULATE` gibt einen skalaren Wert zurück. `CALCULATETABLE` gibt eine Tabelle zurück — nützlich, wenn eine gefilterte Tabelle als Eingabe für eine andere Funktion gebraucht wird:

```dax
Top 5 Produkte =
TOPN(
    5,
    CALCULATETABLE(
        VALUES(Produkt[Bezeichnung]),
        [Gesamtumsatz] > 10000
    ),
    [Gesamtumsatz],
    DESC
)
```

Der Unterschied liegt nicht nur im Rückgabetyp. `CALCULATETABLE` lässt sich dort einsetzen, wo eine Tabelle erwartet wird — etwa als erster Parameter von `SUMX` oder als Filterargument in einem weiteren `CALCULATE`. Für ein einzelnes Measure bleibt `CALCULATE` die richtige Wahl.

## Praxisbeispiel: Regionales Vertriebs-Dashboard

Gesucht ist ein Dashboard für die vier Regionalleiter von Nordlicht. Jeder soll sehen:

- den Umsatz der eigenen Region (folgt dem Regionsfilter)
- den Gesamtumsatz des Unternehmens als Vergleichsgröße (ignoriert den Regionsfilter)
- den Rang der eigenen Region im Vergleich zu allen anderen (alle Regionen müssen sichtbar sein)

```dax
// 1. Regionsumsatz — folgt den Filtern automatisch
Regionsumsatz = [Gesamtumsatz]

// 2. Gesamtumsatz des Unternehmens — entfernt den Regionsfilter
Unternehmen Gesamt =
CALCULATE([Gesamtumsatz], REMOVEFILTERS(Region))

// 3. Rang der Region — vergleicht gegen alle Regionen
Region Rang =
RANKX(
    ALL(Region[RegionName]),
    [Gesamtumsatz],
    ,
    DESC,
    Dense
)
```

Das `ALL(Region[RegionName])` in `RANKX` sorgt dafür, dass die Rangfolge alle Regionen berücksichtigt, nicht nur die gefilterte. Ohne diesen Zusatz wäre jede Region auf Rang 1, weil sie die einzige sichtbare ist.

![Matrix nach Region mit Gesamtumsatz, bezahltem Umsatz und Umsatz per SUMX](/images/tutorials/calculate-function/02-result-matrix.png)

Drei Measures nebeneinander in einer Matrix sind der schnellste Test auf einen Filterfehler: Entspricht `Bezahlter Umsatz` in irgendeiner Zeile dem `Gesamtumsatz`, wird das Filterargument ignoriert.

Ein zweiter Blick lohnt sich auf die Zahlen selbst. Die Nordlicht GmbH erwartet für das Gesamtjahr 48 Mio. €, davon 12,4 Mio. € in der Region Nord. Steht im Dashboard für Nord ein Unternehmensumsatz von 12,4 Mio. € statt 48 Mio. €, fehlt das `REMOVEFILTERS` — ein Fehler, der bei jeder Präsentation auffällt, aber selten vorher.

## CALCULATE debuggen

Liefert `CALCULATE` unerwartete Ergebnisse, hilft diese Reihenfolge:

1. **Filterkontext bestimmen** — was zeigt das Visual, welche Datenschnitte sind aktiv?
2. **Jedes Filterargument prüfen** — ersetzt es einen Filter oder ergänzt es einen?
3. **Auf impliziten Kontextübergang achten** — steht die Formel in einem Iterator?
4. **Die Abfrage in DAX Studio ansehen** — dort ist der Filterkontext an jeder Stelle sichtbar
5. **Mit `ALL()` isolieren** — liefert `CALCULATE([Umsatz], ALL(Vertrieb))` den richtigen Wert, liegt das Problem im Filterkontext, nicht im Ausdruck

In der Praxis hat sich außerdem bewährt, ein Measure testweise ohne Filterargumente zu schreiben und die Differenz zu erklären. Wer den Unterschied zwischen `[Gesamtumsatz]` und `CALCULATE([Gesamtumsatz])` in einer Matrix benennen kann, hat den Filterkontext verstanden.

## Checkliste zum Üben

Vor dem nächsten Schritt sollten Sie:

- [ ] erklären können, warum `CALCULATE` die einzige Funktion ist, die den Filterkontext verändert
- [ ] ein Anteils-Measure mit `ALL` oder `REMOVEFILTERS` schreiben können
- [ ] einen booleschen Filter und ein `FILTER`-Argument in einem `CALCULATE` kombinieren können
- [ ] vorhersagen können, was `CALCULATE([Umsatz], ALL(Vertrieb))` in einer Matrix liefert
- [ ] begründen können, warum `CALCULATE` in `SUMX` das Ergebnis verändert (Kontextübergang)
- [ ] zwischen `ALL`, `ALLSELECTED` und `REMOVEFILTERS` für ein Szenario wählen können

Wer diese Punkte beherrscht, hat die Schwelle vom DAX-Einsteiger zum Fortgeschrittenen überschritten. Der nächste Meilenstein ist die Zeitintelligenz — und die besteht, wie sich zeigt, überwiegend aus `CALCULATE` mit datumsverschobenen Filterargumenten.

## Weiterlesen

- [DAX Grundlagen](/tutorials/de-dax-basics/) — Measures, Filterkontext und die ersten Formeln.
- [Zeitintelligenz in Power BI: YTD, QTD, MTD](/tutorials/de-dax-time-intelligence-ytd-qtd-mtd/) — datumsverschobene Filterargumente richtig aufbauen.
- [DAX CALCULATE: Syntax, Filter Context & Patterns](/tutorials/calculate-function/) — die englische Originalfassung.
- [DAX-Funktionsreferenz](/tools/dax-functions/) — Syntax und Beispiele für 64 Funktionen.
- [PREVIOUSMONTH vs. DATEADD: Warum sie am 31. nicht übereinstimmen](/tutorials/previousmonth-vs-dateadd/)
- [SUMMARIZE vs. SUMMARIZECOLUMNS vs. GROUPBY](/tutorials/summarize-vs-summarizecolumns/)
