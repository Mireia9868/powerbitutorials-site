---
title: "Drillthrough in Power BI einrichten: Felder und Filter"
description: "Drillthrough führt vom Überblick zur Detailseite mit passendem Filterkontext. So legen Sie Felder fest, steuern Filter und bauen den Rückweg ein."
pubDate: 2026-11-18
updatedDate: 2026-11-18
category: "visualization"
difficulty: "Intermediate"
tags: ["drillthrough", "berichtsnavigation", "visualisierung", "filter", "power-bi"]
author: Mireia
featured: false
draft: false
---

Drillthrough gehört zu den wenigen Power-BI-Funktionen, die sich für Anwender sofort selbst erklären: Ein Klick auf einen Balken, und der Bericht springt auf eine Detailseite, die genau diesen Kunden, diesen Monat oder dieses Produkt zeigt. Wer Berichte für den Vertrieb oder das Controlling baut, kommt an dieser Form der Berichtsnavigation kaum vorbei.

Dieser Artikel zeigt, wie Sie Drillthrough einrichten, welche Felder in das Drillthrough-Feld gehören, wie Sie den Filterkontext steuern und welche Entwurfsmuster sich in der Praxis bewährt haben. Die Beispiele stammen aus einem Vertriebsbericht der fiktiven Nordlicht Handel GmbH, dessen Umsätze in Euro ausgewiesen werden.

## So funktioniert Drillthrough

Drillthrough ist eine Verbindung zwischen zwei Berichtsseiten:

1. **Quellseite** — die Übersichtsseite, auf der der Anwender startet.
2. **Zielseite** — die Detailseite, die sich beim Drillthrough öffnet.

Ein Rechtsklick auf einen Datenpunkt der Quellseite und die Auswahl von **Drillthrough → Zielseite** öffnet die Zielseite und übergibt alle Filter aus dem angeklickten Kontext. Danach zeigt die Zielseite nur noch die Datensätze, die zu diesem einen Klick passen.

**Der entscheidende Punkt:** Drillthrough übergibt Filter, keine Klicks. Das Ziel erhält den Filterkontext des Quellvisuals und wendet ihn selbst an. Sie schreiben dafür keine einzige DAX-Zeile — die Konfiguration erfolgt vollständig im Feldbereich.

## Was sind Drillthrough-Felder?

Sobald Sie Drillthrough für eine Seite aktivieren, verlangt Power BI Felder in einem Bereich mit der Bezeichnung **Drillthrough-Felder hier hinzufügen**. Diese Felder sind der gesamte Mechanismus: Sie bestimmen, worauf ein Leser überhaupt springen darf, und sie werden zum Filter, der auf der Zielseite landet.

Drei Dinge sollten Sie wissen, bevor Sie den Bereich füllen.

**Dimensionen hinein, keine Measures.** Die Feldliste der Zielseite entsteht aus diesen Einträgen. Ein Measure besitzt keine unterscheidbaren Werte, nach denen sich filtern ließe — ziehen Sie `Gesamtumsatz` hinein, passiert schlicht nichts.

**Ein Feld ist meistens richtig.** Mit `Produkt` im Bereich bietet ein Rechtsklick auf einen Balken im Kategoriendiagramm den Eintrag „Drillthrough → Produkt" an. Liegen `Produkt` und `Region` gleichzeitig darin, drillt der Leser auf das Feld, das er angeklickt hat; die Zielseite filtert nur nach diesem einen Wert. Das zweite Feld bleibt verfügbar, wird aber nicht angewendet — und genau das verwirrt Anwender, die erwarten, dass beide Filter greifen.

**Wenn das Drillthrough-Menü gar nicht erscheint**, prüfen Sie diese drei Punkte der Reihe nach: Die Zielseite enthält mindestens ein Drillthrough-Feld, die Seite ist nicht ausgeblendet, und das Visual, das Sie anklicken, unterstützt die Funktion. Matrix und Tabelle funktionieren; Karten und KPI-Visuals mit einem einzelnen Wert nicht, weil dort kein Datenpunkt existiert, der den Kontext tragen könnte.

Ein wiederkehrendes Problem in der Praxis: Das Quellvisual zeigt nur den umsatzstärksten Kunden als Balken, der Drillthrough-Filter erwartet aber `Kunde[Kundenname]`. Auch wenn beide dieselbe Information meinen, muss das Feld im Visual vorhanden sein — als Achse, Legende oder in den QuickInfos.

## Drillthrough in Power BI einrichten

### Schritt 1: Zielseite anlegen

1. Fügen Sie dem Bericht eine neue Seite hinzu.
2. Geben Sie ihr einen sprechenden Namen, etwa „Kundendetails".
3. Bauen Sie die Detailvisuals — eine Tabelle mit den Positionen, begleitende Diagramme und Karten mit den wichtigsten Kennzahlen.

### Schritt 2: Drillthrough-Filter hinzufügen

1. Wählen Sie die Zielseite aus und öffnen Sie den Bereich **Filter**.
2. Suchen Sie unten den Abschnitt **Drillthrough**.
3. Ziehen Sie das gewünschte Feld in den Bereich **Drillthrough-Felder hier hinzufügen**.

Ein Beispiel: Sie möchten, dass Anwender auf einen Kundennamen klicken und anschließend alle Bestellungen dieses Kunden sehen. Dann ziehen Sie `Kunde[Kundenname]` in den Drillthrough-Bereich. Die Zielseite zeigt danach nur noch Positionen der Nordlicht Handel GmbH, deren Bestellungen zwischen dem 01.09.2026 und dem 30.09.2026 liegen — abhängig davon, welchen Kontext der Klick mitbringt.

**Mehrere Felder sind möglich:** Legen Sie `Kunde[Kundenname]` und `Datum[Jahr]` gemeinsam hinein, filtert die Zielseite nach beiden Werten. Ein Klick auf einen Balken im Jahr 2026 zeigt dann ausschließlich die Bestellungen dieses Kunden aus 2026.

### Schritt 3: Von der Quellseite aus testen

1. Wechseln Sie auf die Übersichtsseite.
2. Klicken Sie mit der rechten Maustaste auf einen Datenpunkt, der das Drillthrough-Feld enthält.
3. Wählen Sie **Drillthrough** und anschließend den Namen der Zielseite.
4. Die Zielseite öffnet sich, gefiltert auf den Kontext des angeklickten Punkts.

Prüfen Sie dabei auch den Fall, dass mehrere Ausprägungen angeklickt werden: Markieren Sie zwei Kunden gleichzeitig, muss die Zielseite beide zeigen — sonst ist der Filter falsch konfiguriert.

## Die Zurück-Schaltfläche

Beim Drillthrough fügt Power BI oben links automatisch eine Zurück-Schaltfläche ein. Ein Klick darauf bringt den Anwender auf die Quellseite zurück.

**Schaltfläche anpassen:**

1. Wählen Sie die Schaltfläche aus — sie erscheint als eigenes Visual auf der Seite.
2. Ändern Sie im Bereich **Format** Symbol, Text und Hintergrund.
3. Alternativ legen Sie eine eigene Schaltfläche mit dem Aktionstyp **Zurück** an, um das Aussehen vollständig zu kontrollieren.

**Warnung:** Löschen Sie die automatisch erzeugte Schaltfläche, ohne Ersatz anzulegen, bleibt dem Anwender nur der Seitenreiter — und der ist auf Mobilgeräten oft ausgeblendet. Eine sichtbare Rücknavigation gehört auf jede Drillthrough-Seite.

## Alle Filter übergeben oder nur einzelne Felder

Standardmäßig übergibt Drillthrough ausschließlich die Felder, die Sie in den Drillthrough-Bereich gelegt haben. Sie können aber auch sämtliche Filter der Quellseite mitnehmen:

1. Öffnen Sie auf der Zielseite den Bereich **Filter**.
2. Suchen Sie im Abschnitt **Drillthrough** den Schalter **Alle Filter beibehalten**.
3. Schalten Sie ihn ein, um alle aktiven Filter der Quellseite zu übergeben.
4. Schalten Sie ihn aus, um nur die Felder aus dem Drillthrough-Bereich zu übernehmen.

**Wann sich „Alle Filter beibehalten" lohnt:**

- **Ein:** wenn die Zielseite den vollständigen Kontext des Anwenders abbilden soll — Datenschnitte, visuelle Filter und Seitenfilter eingeschlossen.
- **Aus:** wenn ausschließlich der Kontext des Drillthrough-Felds zählen soll und alles andere bewusst ignoriert wird.

In den meisten Berichten ist die eingeschaltete Variante die bessere Wahl. Wer im Datenschnitt „Region: Nord" ausgewählt hat, erwartet auch auf der Detailseite nur norddeutsche Kunden — nicht plötzlich bundesweite Zahlen.

## Berichtsübergreifender Drillthrough

Mit berichtsübergreifendem Drillthrough springt der Anwender von einem Bericht in einem Arbeitsbereich zu einem Bericht in einem anderen Arbeitsbereich. Das ist nützlich, wenn verschiedene Teams eigene Berichte pflegen, die sich eine gemeinsame Dimension teilen — etwa Vertrieb und Logistik, die beide auf `Kunde[Kundenname]` arbeiten.

### Einrichtung

1. Öffnen Sie in Power BI Desktop **Datei → Optionen → Berichtseinstellungen**.
2. Aktivieren Sie **Visuals in diesem Bericht dürfen Drillthrough auf andere Berichte verwenden**.
3. Fügen Sie auf der Zielseite des Zielberichts das Drillthrough-Feld im Filterbereich hinzu — wie beim normalen Drillthrough.
4. Veröffentlichen Sie beide Berichte im Dienst.
5. Klicken Sie auf der Quellseite mit der rechten Maustaste auf einen Datenpunkt → **Drillthrough** → der Zielbericht erscheint im Menü.

**Voraussetzungen:**

- Beide Berichte liegen in Arbeitsbereichen, auf die der Anwender Zugriff hat.
- Beide Berichte verwenden denselben Feldnamen; das Drillthrough-Feld muss in beiden Datenmodellen existieren.
- Der Zielbericht muss im Power BI Dienst veröffentlicht sein — im reinen Desktop-Betrieb funktioniert es nicht.

## Bewährte Entwurfsmuster

### Muster 1: Von der Übersicht zum Transaktionsdetail

Das häufigste Muster. Eine Übersichtsseite zeigt aggregierte Kennzahlen, die Detailseite listet die einzelnen Positionen.

**Übersichtsseite:** Balkendiagramm Umsatz je Kunde
**Zielseite:** Tabelle mit Belegnummer, Bestelldatum, Betrag, Produkt und Menge
**Drillthrough-Feld:** `Kunde[Kundenname]`

Setzen Sie oben auf die Zielseite eine Karte mit Kundenname und Gesamtumsatz — sie orientiert den Anwender unmittelbar nach dem Sprung:

```dax
// Anzeige auf der Zielseite
Ausgewählter Kunde =
SELECTEDVALUE ( Kunde[Kundenname], "Mehrere Kunden" )
```

### Muster 2: Drillthrough mit dynamischem Titel

Machen Sie die Zielseite selbsterklärend, indem Sie anzeigen, worauf gedrillt wurde:

1. Legen Sie ein Measure an, das den Drillthrough-Kontext aufnimmt:

```dax
Drillthrough-Titel =
VAR Kunde = SELECTEDVALUE ( Kunde[Kundenname] )
VAR Produkt = SELECTEDVALUE ( Produkt[Produktname] )
RETURN
    "Details für "
        & IF ( ISBLANK ( Kunde ), "alle Kunden", Kunde )
        & IF ( ISBLANK ( Produkt ), "", " – " & Produkt )
```

2. Fügen Sie ein Textfeld auf der Zielseite ein.
3. Verknüpfen Sie das Textfeld mit diesem Measure über die Option **Feld** in der Formatierung.

Der Titel zeigt dann „Details für Nordlicht Handel GmbH – Kompaktanlage" statt eines statischen „Kundendetails", das bei jedem Sprung gleich aussieht.

### Muster 3: Mehrere Ziele aus einem Visual

Ein einzelnes Visual kann mehrere Drillthrough-Ziele bedienen. Verteilen Sie dazu Felder auf die Drillthrough-Bereiche verschiedener Seiten:

- Seite „Kundendetails" drillt über `Kunde[Kundenname]`.
- Seite „Produktdetails" drillt über `Produkt[Produktname]`.

Beim Rechtsklick sieht der Anwender beide Einträge im Drillthrough-Menü und entscheidet selbst, welche Detailtiefe er braucht. Das ist besonders hilfreich, wenn ein und dieselbe Umsatzzahl je nach Frage eine andere Antwort verlangt.

### Muster 4: Drillthrough per Schaltfläche

Statt eines Rechtsklicks lässt sich Drillthrough auch über eine Schaltfläche auslösen:

1. Legen Sie ein Schaltflächen-Visual auf der Quellseite an.
2. Setzen Sie den Aktionstyp auf **Drillthrough**.
3. Wählen Sie als Ziel die gewünschte Seite.
4. Die Schaltfläche bleibt ausgegraut, bis der Anwender einen Datenpunkt markiert.
5. Sobald ein Balken oder eine Zeile ausgewählt ist, wird sie aktiv.

Für Anwender, die Power BI nicht täglich nutzen, ist das deutlich auffindbarer als ein Rechtsklick — und auf Touch-Geräten ohnehin die einzige verlässliche Variante.

## Häufige Fehler

### 1. Der Drillthrough-Eintrag erscheint nicht

**Ursache:** Das Quellvisual enthält das Drillthrough-Feld in keiner Rolle — weder als Achse noch als Legende oder in den QuickInfos.

**Lösung:** Das Feld muss in der Feldkonfiguration des Visuals vorkommen. Wer nach Kunde drillen möchte, muss `Kunde[Kundenname]` irgendwo im Quellvisual unterbringen, notfalls als QuickInfo.

### 2. Die Zielseite zeigt alle Daten, der Filter greift nicht

**Ursache:** Das Feld im Quellvisual und das Feld im Drillthrough-Bereich stimmen nicht überein. Das passiert häufig, wenn dieselbe Spalte in mehreren Tabellen existiert.

**Lösung:** Stellen Sie sicher, dass beide Seiten dasselbe Feld aus derselben Tabelle verwenden. Greift das Visual auf `Vertrieb[Kundenname]` zu, der Drillthrough-Bereich aber auf `Kunde[Kundenname]`, wird der Filter nicht übergeben.

### 3. Drillthrough läuft im Desktop, aber nicht im Dienst

**Ursache:** Berichtsübergreifender Drillthrough setzt veröffentlichte Berichte voraus. Beim normalen Drillthrough bricht die Verbindung, wenn die Zielseite nach dem Veröffentlichen umbenannt wurde.

**Lösung:** Veröffentlichen Sie den Bericht erneut. Bleibt das Problem bestehen, entfernen Sie das Drillthrough-Feld auf der Zielseite und fügen Sie es neu hinzu.

### 4. Zu viele Filter landen auf der Zielseite

**Ursache:** „Alle Filter beibehalten" ist aktiv, und die Quellseite enthält zahlreiche Datenschnitte. Die Zielseite erhält sie alle und filtert die Ergebnisse dadurch zu stark.

**Lösung:** Schalten Sie „Alle Filter beibehalten" aus und legen Sie nur die tatsächlich benötigten Felder in den Drillthrough-Bereich. Alternativ heben Sie unerwünschte Filter auf der Zielseite mit `REMOVEFILTERS` auf.

## Drillthrough, Drilldown und Erweitern im Vergleich

Die drei Funktionen klingen ähnlich, tun aber grundlegend Verschiedenes:

| Funktion | Was sie macht | Wann sinnvoll |
|---|---|---|
| **Drillthrough** | Springt auf eine andere Seite, gefiltert auf den angeklickten Kontext | Übersicht → Detail über unterschiedliche Seitenlayouts |
| **Drilldown** | Öffnet die nächste Ebene einer Hierarchie im selben Visual (Jahr → Quartal → Monat) | Hierarchische Daten in einem Visual erkunden |
| **Erweitern** | Zeigt alle Ebenen einer Hierarchie gleichzeitig | Schneller Blick auf die gesamte Hierarchie |

Drillthrough wechselt die Seite. Drilldown wechselt die Ebene innerhalb eines Visuals. Erweitern zeigt alles auf einmal.

## FAQ

### Q: Funktioniert Drillthrough auch aus einer Matrix?

Ja. Klicken Sie mit der rechten Maustaste auf eine Zelle der Matrix und wählen Sie **Drillthrough**. Die Zielseite erhält den Filterkontext genau dieser Zelle, einschließlich aller Zeilen- und Spaltengruppierungen.

### Q: Lässt sich ein Measure-Wert per Drillthrough übergeben?

Nein. Drillthrough übergibt Felder, also Dimensionen, keine Measures. Wenn die Zielseite Daten zu einem bestimmten Kennzahlenbereich zeigen soll, filtern Sie das Quellvisual auf diesen Bereich und drillen Sie anschließend.

### Q: Wie viele Drillthrough-Felder sind sinnvoll?

Eine harte Obergrenze gibt es nicht, doch jedes weitere Feld verengt den Kontext der Zielseite. In der Praxis haben sich zwei bis drei Felder bewährt. Mehr davon, und Anwender verstehen nicht mehr, warum die Detailseite zeigt, was sie zeigt.

### Q: Funktioniert Drillthrough in Power BI Mobile?

Ja, aber Rechtsklicks gibt es auf Mobilgeräten nicht. Nutzen Sie den schaltflächengesteuerten Drillthrough aus Muster 4. Nach dem Markieren eines Datenpunkts löst ein Tippen auf die Schaltfläche den Sprung aus.

## Weiterführende Anleitungen

- [Bedingte Formatierung in Power BI](/tutorials/de-conditional-formatting-power-bi/) — Farben und Regeln, die auch auf Detailseiten für Orientierung sorgen.
- [Power BI Performance-Optimierung](/tutorials/de-power-bi-performance-optimization/) — damit Drillthrough-Seiten auch bei großen Modellen schnell öffnen.
- [Power BI Drill Through (englische Originalfassung)](/tutorials/power-bi-drill-through/) — die englische Version dieses Artikels.

Die technische Referenz finden Sie bei Microsoft unter [Drillthrough in Power BI](https://learn.microsoft.com/de-de/power-bi/create-reports/desktop-drillthrough).
