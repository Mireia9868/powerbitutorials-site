---
title: "Kalendertabelle in Power BI erstellen: 3 Methoden und die entscheidenden Spalten"
description: "Ohne lückenlose Kalendertabelle liefert die Zeitintelligenz falsche Werte. Drei Wege zum Aufbau, die Pflichtspalten und der Schritt, den viele vergessen."
pubDate: 2026-11-25
updatedDate: 2026-11-25
category: "time-intelligence"
difficulty: "Beginner"
tags: ["kalendertabelle", "datumsdimension", "zeitintelligenz", "power-bi", "dax"]
author: Mireia
featured: false
draft: false
---

Eine Kalendertabelle ist das Rückgrat jedes Power-BI-Modells, das Zeitintelligenz braucht. Fehlt sie, liefern Funktionen wie `TOTALYTD`, `SAMEPERIODLASTYEAR` und `DATEADD` entweder einen Fehler oder Werte, die plausibel aussehen und trotzdem falsch sind. Die gute Nachricht: Der Aufbau dauert wenige Minuten, und Power BI bietet drei solide Wege — je nach Datenquelle und gewünschtem Grad an Kontrolle.

Diese Anleitung zeigt alle drei Methoden: die berechnete Tabelle mit `CALENDAR`/`CALENDARAUTO`, die Variante in Power Query (M) und die automatische Datums-/Zeitangabe für schnelle Prototypen. Dazu kommt das Markieren als Datumstabelle und die Fehler, nach denen Zeitintelligenz-Maßnahmen plötzlich leer bleiben. Die Referenz zu allen Datumsfunktionen finden Sie in der [DATE-Dokumentation von Microsoft](https://learn.microsoft.com/de-de/dax/date-function-dax).

## Warum eine eigene Kalendertabelle nötig ist

Eine Faktentabelle speichert in der Regel ein Buchungsdatum. Diese Spalte enthält Tausende Duplikate und Lücken an Tagen ohne Umsatz. Ziehen Sie sie in ein Visual, erzeugt Power BI eine implizite Hierarchie (Jahr > Quartal > Monat > Tag) — aber für fehlende Tage existieren keine Zeilen. Jede Kennzahl, die eine lückenlose Zeitachse voraussetzt, bricht: laufende Summen, Vorjahresvergleiche, YTD-Auswertungen.

Eine echte Kalendertabelle löst das mit genau einer Zeile pro Tag, ohne Lücken, über einen Bereich, der alle Fakten-Daten plus Puffer für Vergleichsperioden abdeckt. Außerdem lassen sich Spalten ergänzen, die Power BI nicht spontan ableiten kann: Geschäftsjahre, Arbeitstag-Kennzeichen, eigene Monatssortierung, relative Datumsoffsets.

Die Anforderungen an eine Tabelle, die Power BI als Datumstabelle akzeptiert, sind exakt:

- eine Spalte vom Datentyp **Datum** (oder Datum/Uhrzeit) mit eindeutigen Werten,
- ein **lückenloser** Bereich ohne fehlende Tage,
- alle Datumswerte innerhalb desselben Kalenderjahres — oder die Tabelle ist als Datumstabelle markiert,
- keine leeren Datumswerte,
- Beziehungen von den Faktentabellen laufen über diese Datumsspalte.

## Methode 1: Berechnete Tabelle mit CALENDAR

Der schnellste Weg — er funktioniert in jedem Modell, unabhängig davon, ob Sie Import oder DirectQuery verwenden. Öffnen Sie **Modellieren > Neue Tabelle** und fügen Sie ein:

```dax
Kalender =
VAR StartDatum = DATE(2022, 1, 1)
VAR EndDatum   = DATE(2026, 12, 31)
RETURN
ADDCOLUMNS(
    CALENDAR(StartDatum, EndDatum),
    "Jahr",             YEAR([Date]),
    "Quartal",          "Q" & QUARTER([Date]),
    "Monatsnummer",     MONTH([Date]),
    "Monatsname",       FORMAT([Date], "MMMM"),
    "MonatsKurz",       FORMAT([Date], "MMM"),
    "Jahr-Monat",       FORMAT([Date], "YYYY-MM"),
    "Wochentag",        FORMAT([Date], "dddd"),
    "WochentagNr",      WEEKDAY([Date], 2),
    "Sortierschluessel", YEAR([Date]) * 100 + MONTH([Date])
)
```

`CALENDAR` liefert eine einspaltige Tabelle von `StartDatum` bis `EndDatum` einschließlich. `ADDCOLUMNS` hängt die beschreibenden Spalten an. Die Spalte `Sortierschluessel` wirkt unscheinbar, ist aber zentral: Ohne numerischen Sortierschlüssel sortiert Power BI „April“ alphabetisch vor „August“ — in jedem Diagramm falsch, das nicht direkt die Monatsnummer verwendet.

Eine Alternative ist `CALENDARAUTO()`. Sie durchsucht alle Datumsspalten im Modell und erzeugt einen Bereich vom frühesten bis zum spätesten gefundenen Wert:

```dax
Kalender =
ADDCOLUMNS(
    CALENDARAUTO(12),
    "Jahr", YEAR([Date]),
    "Monatsnummer", MONTH([Date]),
    "Monatsname", FORMAT([Date], "MMMM"),
    "Sortierschluessel", YEAR([Date]) * 100 + MONTH([Date])
)
```

Das Argument `12` sagt Power BI, dass das Geschäftsjahr im Dezember endet; der Bereich wird bis zum Ende dieses Geschäftsjahres verlängert. In deutschen Unternehmen endet das Geschäftsjahr oft am 31.12., manchmal aber am 30.09. oder 31.03. — dann müssen Sie den Wert entsprechend anpassen. `CALENDARAUTO` ist bequem, wird aber bei jeder Aktualisierung neu berechnet und kann einen völlig anderen Bereich erzeugen, wenn in einer Nachschlagetabelle ein einzelnes Datum aus 1999 liegt. Für Produktionsmodelle sollten Sie den Bereich fest vorgeben.

Weil es sich um eine berechnete Tabelle handelt, läuft sie beim Aktualisieren als DAX-Abfrage. In Import-Modellen ist das vernachlässigbar. In DirectQuery werden berechnete Tabellen in das Modell materialisiert; sie funktionieren weiterhin, kosten aber einen Verarbeitungsschritt.

## Methode 2: Power Query (M)

Wenn Sie die Kalendertabelle lieber in der ETL-Schicht steuern oder dieselbe Tabelle in mehreren Modellen wiederverwenden wollen, bauen Sie sie in Power Query. Erstellen Sie eine **leere Abfrage** und fügen Sie im Erweiterten Editor ein:

```powerquery
let
    StartDatum = #date(2022, 1, 1),
    EndDatum   = #date(2026, 12, 31),
    Tage       = Duration.Days(EndDatum - StartDatum) + 1,
    DatumsListe = List.Dates(StartDatum, Tage, #duration(1, 0, 0, 0)),
    AlsTabelle = Table.FromList(DatumsListe, Splitter.SplitByNothing(), {"Datum"}),
    Typisiert  = Table.TransformColumnTypes(AlsTabelle, {{"Datum", type date}}),
    MitJahr    = Table.AddColumn(Typisiert, "Jahr", each Date.Year([Datum]), Int64.Type),
    MitMonat   = Table.AddColumn(MitJahr, "Monatsnummer", each Date.Month([Datum]), Int64.Type),
    MitMonatsname = Table.AddColumn(MitMonat, "Monatsname", each Date.ToText([Datum], "MMMM"), type text),
    MitQuartal = Table.AddColumn(MitMonatsname, "Quartal", each "Q" & Text.From(Date.QuarterOfYear([Datum])), type text),
    MitJahrMonat = Table.AddColumn(MitQuartal, "Jahr-Monat", each Date.ToText([Datum], "yyyy-MM"), type text),
    MitSortierschluessel = Table.AddColumn(MitJahrMonat, "Sortierschluessel",
                              each Date.Year([Datum]) * 100 + Date.Month([Datum]), Int64.Type)
in
    MitSortierschluessel
```

Benennen Sie die Abfrage `Kalender` und laden Sie sie. Die M-Variante hat mehrere Vorteile:

- Die Logik liegt in der Quellschicht und ist versionierbar sowie wiederverwendbar.
- `StartDatum` und `EndDatum` lassen sich als Parameter aus einer eigenen Abfrage steuern.
- Die Aktualisierungskosten laufen im normalen Abfrage-Pipeline mit, statt eine DAX-Tabelle zu materialisieren.

Ein Punkt zum Aufpassen: `List.Dates` mit einer Dauer von einem Tag erzeugt den exakt inklusiven Bereich. Ein Rechenfehler an dieser Stelle ist die häufigste Ursache dafür, dass eine Power-Query-Kalendertabelle am Ende um einen Tag danebenliegt.

<div class="tool-embed">
  <p><strong>Die DAX-Version lieber generieren lassen?</strong> Der Kalendertabellen-Generator baut dieselbe Tabelle — Zeitraum wählen, ISO-Wochen und Geschäftsjahr umschalten, dann DAX- oder Power-Query-Code kopieren.</p>
  <details>
    <summary>Generator öffnen</summary>
    <iframe data-pbt="pbt-default" src="https://powerbitutorials.com/embed/date-table/?ref=powerbitutorials.com"
      width="100%" height="640" loading="lazy"
      style="border:1px solid #e5e3d8;border-radius:10px;max-width:960px"
      title="Power BI Kalendertabellen-Generator"></iframe>
  </details>
  <p style="margin-top:10px;font-size:0.85rem;color:var(--c-text-dim)">
    Erst den Code verstehen? Die Ausgabe des Generators nutzt dasselbe Muster aus
    <code>CALENDAR</code> und <code>ADDCOLUMNS</code> wie Methode 1 — die Oberfläche des Tools ist englisch.
  </p>
</div>

## Methode 3: Automatische Datums-/Zeitangabe (nur für Prototypen)

Power BI hat eine versteckte Funktion namens **Automatische Datums-/Zeitangabe**. Ist sie aktiv, erhält jede Datumsspalte im Modell eine unsichtbare Kalendertabelle, und die implizite Hierarchie in den Visuals funktioniert tatsächlich für Zeitintelligenz.

Ein- und ausschalten lässt sich das unter **Datei > Optionen und Einstellungen > Optionen > Daten laden**. In neuen Dateien ist die Funktion standardmäßig aktiv.

Der Haken: Die automatische Datums-/Zeitangabe erzeugt eine verborgene Tabelle **pro Datumsspalte**. Ein Modell mit zehn Datumsspalten in mehreren Faktentabellen schleppt zehn Kalendertabellen mit — jede belegt Speicher und vergrößert Modellgröße sowie Aktualisierungsdauer. Die Empfehlung von Microsoft lautet, die Funktion abzuschalten, sobald eine echte Kalendertabelle vorhanden ist. Nutzen Sie sie nur beim Erkunden eines neuen Datensatzes, bauen Sie danach eine richtige Kalendertabelle und schalten Sie sie aus.

## Als Datumstabelle markieren

Nach dem Aufbau müssen Sie Power BI noch sagen, dass die Tabelle eine Datumstabelle ist. Wählen Sie die Tabelle `Kalender`, gehen Sie auf **Tabellentools > Als Datumstabelle markieren** und wählen Sie die Spalte `Datum`. Das schaltet das Feld `Datum` für Zeitintelligenz-Funktionen frei, entfernt die automatische Hierarchie und lässt Power BI prüfen, ob alle Datumswerte der Faktentabellen in der Kalendertabelle vorkommen.

Danach folgen die Beziehungen. Ziehen Sie in der Modellansicht `Kalender[Datum]` auf die Datumsspalte jeder Faktentabelle. Die Kardinalität sollte eins-zu-viele sein (Kalendertabelle auf der Eins-Seite), mit einer einzigen Filterrichtung — das ist die übliche Sternschema-Praxis.

Verknüpfen Sie eine Faktentabelle nicht gleichzeitig mit mehreren Datumsspalten. Enthält eine Faktentabelle `BestellDatum` und `LieferDatum`, legen Sie entweder zwei Rollenspiel-Beziehungen mit Bedacht an oder aktivieren die inaktive Beziehung in einem Measure per `USERELATIONSHIP`.

## Typische Fehler

| Symptom | Wahrscheinliche Ursache |
|---|---|
| `TOTALYTD` liefert leer | Tabelle nicht als Datumstabelle markiert oder keine aktive Beziehung |
| Monate alphabetisch sortiert | Numerischer Sortierschlüssel fehlt; **Nach Spalte sortieren** auf den Monatsnamen anwenden |
| Werte fehlen für einzelne Tage | Datumsbereich deckt nicht alle Fakten-Daten ab |
| Doppelte Datumswerte | `SELECTEDVALUE` oder ein Join in der DAX-Tabelle statt `CALENDAR` verwendet |
| Modell wird immer größer | Automatische Datums-/Zeitangabe läuft zusätzlich zur manuellen Kalendertabelle |

Ein weiterer Stolperstein: Verwenden Sie `EARLIER` nicht in den berechneten Spalten der Kalendertabelle, wenn kein verschachtelter Zeilenkontext zum Vergleichen existiert. `EARLIER` verweist auf einen äußeren Zeilenkontext und wirft außerhalb eines solchen einen Fehler. Für Kalendertabellen erledigen `ADDCOLUMNS` und `CALENDAR` alles Nötige ohne `EARLIER`.

Sobald die Kalendertabelle steht, wird jede Zeitintelligenz-Kennzahl geradlinig. Dort ergänzen Sie auch Geschäftskalender-Logik, Arbeitstag-Kennzeichen und relative Datumsmarker — was sich in dem Moment bezahlt macht, in dem jemand einen rollierenden 13-Wochen-Bericht verlangt.

## Wenn die Kalendertabelle im Datenschnitt nicht filtert

Ein Datenschnitt, der die richtigen Jahre anzeigt, aber nichts filtert, ist fast immer ein Beziehungs- oder Feldproblem — kein DAX-Problem. Arbeiten Sie diese Prüfungen der Reihe nach ab; das ist die schnellste Fehlerbehebung:

1. **Als Datumstabelle markiert?** Tabelle auswählen → **Tabellentools → Als Datumstabelle markieren** und die lückenlose Spalte `Datum` wählen. Zeitintelligenz und Datumsfilter verlassen sich auf dieses Kennzeichen.
2. **Aktive Beziehung zur Faktentabelle?** In der **Modellansicht** prüfen, ob eine durchgezogene (aktive) Linie von `Kalender[Datum]` zur Datumsspalte der Faktentabelle führt. Eine gestrichelte Linie ist inaktiv — Datumsfilter fließen erst, wenn Sie sie aktivieren oder `USERELATIONSHIP` verwenden.
3. **Wird die Spalte der Kalendertabelle im Visual verwendet?** Der Datenschnitt muss `Kalender[Datum]` (oder eine daraus gebildete Hierarchie) nutzen, nicht `Vertrieb[BestellDatum]`. Das direkte Filtern der Faktenspalte umgeht die markierte Tabelle.
4. **Deckt der Bereich die Fakten ab?** Eine `CALENDAR`-Tabelle ab 2024 filtert keine Zeilen aus 2023. Bauen Sie sie aus den Daten mit `CALENDAR ( MIN ( Vertrieb[BestellDatum] ), MAX ( Vertrieb[BestellDatum] ) )` oder erweitern Sie die festen Grenzen.
5. **Automatische Datums-/Zeitangabe noch aktiv?** **Datei → Optionen → Daten laden → Zeitintelligenz** — schalten Sie die automatische Datums-/Zeitangabe aus, damit verborgene Kalendertabellen nicht mit Ihrer konkurrieren.

Wenn alle fünf Punkte passen und der Datenschnitt trotzdem nichts bewirkt, prüfen Sie **Interaktionen bearbeiten** zwischen Datenschnitt und Visual und testen Sie in einem neuen Bericht mit einem einzelnen Tabellenvisual, um das Modell vom Seitendesign zu trennen.

## FAQ

### F: Berechnete DAX-Tabelle oder Power-Query-Tabelle?

Nehmen Sie Power Query, wenn Ihre Quelle das unterstützt und die Logik außerhalb des Modells liegen soll. Für Tempo und Einfachheit ist eine berechnete DAX-Tabelle sinnvoll, besonders in kleinen und mittleren Modellen. Beide performen bei der Aktualisierung gut; der Unterschied liegt vor allem in der Wartbarkeit und darin, wo Ihr Team Transformationen erwartet.

### F: Welchen Datumsbereich sollte die Kalendertabelle abdecken?

Decken Sie das früheste und späteste vollständige Jahr Ihrer Faktentabellen ab und verlängern Sie beide Enden um ein volles Jahr, damit `SAMEPERIODLASTYEAR` und `SAMEPERIODNEXTYEAR` Daten zum Rechnen haben. Ein Bereich 2022–2026 passt zu einem Modell, dessen Fakten von 2023 bis 2025 laufen.

### F: Ist die automatische Datums-/Zeitangabe jemals die richtige Wahl?

Für einen schnellen Ad-hoc-Bericht auf einem Ein-Tabellen-Modell spart sie Einrichtungszeit. Alles, was Sie teilen, veröffentlichen oder weiterentwickeln wollen, braucht eine manuelle Kalendertabelle — und in dieser Datei sollte die automatische Datums-/Zeitangabe aus sein.

### F: Brauche ich separate Datumsspalten für Geschäftsjahre?

Nein. Ergänzen Sie in der einen Kalendertabelle zusätzliche Spalten für Geschäftsjahr, Geschäftsquartal und Geschäftsperiode und markieren Sie sie bei Bedarf als Sortierspalten. Eine einzige Kalendertabelle hält das Modell sauber und die Beziehungen einfach.

### F: Warum liefert meine Zeitintelligenz-Kennzahl in jeder Zeile denselben Wert?

Das bedeutet fast immer, dass die im Visual verwendete Datumsspalte aus der Faktentabelle stammt statt aus der markierten Kalendertabelle. Tauschen Sie sie gegen `Kalender[Datum]` oder eine daraus gebildete Hierarchiespalte.

Wer das lieber von Hand baut: Das [Time Intelligence Starter Pack](/resources/time-intelligence-starter/) enthält das Skript für die Kalendertabelle und die zwölf Kennzahlen, die darauf laufen — kostenlos, ohne Konto.

## Weiterlesen

- [Zeitintelligenz in Power BI: YTD, QTD und MTD](/tutorials/de-dax-time-intelligence-ytd-qtd-mtd/) — die Kennzahlen, die auf dieser Kalendertabelle aufsetzen.
- [DAX Grundlagen](/tutorials/de-dax-basics/) — Measures, Filterkontext und die ersten Formeln.
- [Create a Date Table in Power BI (3 Methods)](/tutorials/power-bi-date-table/) — die englische Originalfassung dieses Artikels.
- [Sternschema und Datenmodellierung](/tutorials/data-modeling-star-schema/)
- [DirectQuery vs. Import-Modus](/tutorials/directquery-vs-import-mode/)
- [PREVIOUSMONTH vs. DATEADD: Warum sie am 31. nicht übereinstimmen](/tutorials/previousmonth-vs-dateadd/)
