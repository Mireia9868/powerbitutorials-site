---
title: "DAX Grundlagen: Measures, Filterkontext und die ersten Formeln"
description: "Was DAX ist, warum Measures und berechnete Spalten nicht austauschbar sind und welche fünf Formeln Sie am ersten Tag schreiben sollten — inklusive der Regeln dahinter."
pubDate: 2026-11-19
updatedDate: 2026-11-19
category: "dax"
difficulty: "Beginner"
tags: ["dax", "dax-grundlagen", "measures", "berechnete-spalten", "filterkontext"]
author: Mireia
featured: false
draft: false
---

Wer einen Power-BI-Bericht gebaut hat und an den Punkt kommt, an dem Drag-and-drop-Visuals nicht mehr ausreichen, steht genau dort, wo DAX unverzichtbar wird. Diese Anleitung erklärt die Grundlagen, die jeder Analyst vor dem ersten fortgeschrittenen Muster braucht — einschließlich der Fehler, über die die meisten Einsteiger stolpern, und eines durchgerechneten Beispiels zum Mitmachen.

![Formelleiste in Power BI mit dem Measure Gesamtumsatz, SUM(Vertrieb[Umsatz])](/images/tutorials/dax-basics/01-measure-formula-bar.png)

![Matrix mit Gesamtumsatz je Region im Vergleich zu Bezahltem Umsatz und Umsatz per SUMX](/images/tutorials/dax-basics/02-result-matrix.png)

![Performance Analyzer misst die Ladezeit des Matrix-Visuals in Power BI Desktop](/images/tutorials/dax-basics/03-performance-analyzer.png)

## Was ist DAX?

DAX (Data Analysis Expressions) ist die Formelsprache hinter Power BI, Power Pivot für Excel und tabellarischen Analysis-Services-Modellen. Die Syntax erinnert an Excel-Formeln, das Verhalten ist aber grundlegend anders, weil DAX über **Tabellen und Spalten** rechnet und nicht über Zellen.

Die wichtigste gedankliche Umstellung: **DAX wertet eine gefilterte Tabelle aus, keinen Zellbereich.** Jedes Measure, das Sie schreiben, läuft in einem *Filterkontext* — also in der Menge der Zeilen, die aufgrund von Datenschnitten, Kreuzfilterung im Visual und Beziehungen im Datenmodell gerade sichtbar sind.

Deshalb kann dasselbe Measure in verschiedenen Visuals unterschiedliche Zahlen liefern, ohne dass Sie an der Formel etwas ändern. Ein Measure `[Gesamtumsatz]` zeigt auf einer Karte den Gesamtwert. Dasselbe Measure in einer nach Produktkategorie gruppierten Matrix zeigt den Umsatz je Kategorie — weil die Matrix einen Filterkontext anwendet, der die sichtbaren Zeilen jeweils auf eine Kategorie eingrenzt.

## Measures und berechnete Spalten

Das ist die erste Entscheidung, die Sie bei jeder DAX-Formel treffen, und genau hier scheitern die meisten Einsteiger.

| Aspekt | Measure | Berechnete Spalte |
|--------|---------|-------------------|
| Berechnungszeitpunkt | Bei der Abfrage (im Visual) | Bei der Aktualisierung der Daten |
| Speicherung | Wird nicht gespeichert — on demand berechnet | Wird im Modell gespeichert (belegt Arbeitsspeicher) |
| Filterkontext | Dynamisch, abhängig vom Visual | Nur Zeilenkontext (die aktuelle Zeile) |
| Typischer Einsatz | Aggregationen: SUM, AVERAGE, COUNT | Attribute je Zeile: `Preis * Menge` |
| Auswirkung auf die Performance | Vernachlässigbar (pro Abfrage berechnet) | Vergrößert das Modell, verlangsamt die Aktualisierung |

**Faustregel:** Hängt das Ergebnis vom Filterkontext des Visuals ab, schreiben Sie ein Measure. Ist das Ergebnis für jede Zeile gleich, unabhängig von Filtern, schreiben Sie eine berechnete Spalte.

> **Häufiger Fehler:** Zu viele berechnete Spalten sind die häufigste Ursache für aufgeblähte Power-BI-Modelle. Eine berechnete Spalte liegt im VertiPaq-Engine-Speicher und belegt für jede Zeile Arbeitsspeicher — bei einer Faktentabelle mit 50 Millionen Zeilen kann eine einzige zusätzliche Spalte die Datei um mehrere hundert Megabyte vergrößern. Setzen Sie standardmäßig auf Measures, außer Sie benötigen den Wert wirklich je Zeile.

### Wann sich eine berechnete Spalte lohnt

- **Gruppierung und Bänderung** — etwa eine Spalte `Preisband` („Niedrig", „Mittel", „Hoch"), nach der Sie immer wieder filtern oder schneiden
- **Schlüsselspalten für Beziehungen** — das Verketten von Feldern zu einem eindeutigen Schlüssel
- **Statische Attribute** — Werte, die sich durch den Filterkontext nie ändern (zum Beispiel `Kundenstufe` auf Basis des Lebenszeitumsatzes)

Wenn Sie in einer berechneten Spalte `CALCULATE` schreiben, um auf eine andere Tabelle zu verweisen, wollen Sie in der Regel ein Measure.

## Praxisbeispiel: ein Vertriebsbericht

Gehen wir ein realistisches Beispiel durch. Angenommen, es gibt eine Tabelle `Vertrieb` mit den Spalten `Umsatz`, `Menge`, `Stückkosten` und `Bestelldatum` sowie eine Dimensionstabelle `Produkte`, die über `Produktschlüssel` verbunden ist. Die fiktive Rheinwerk Technik GmbH verkauft Kompaktanlagen und weist alle Beträge in Euro aus.

**Gesamtumsatz:**

```dax
Gesamtumsatz = SUM(Vertrieb[Umsatz])
```

**Gesamtmenge:**

```dax
Gesamtmenge = SUM(Vertrieb[Menge])
```

**Durchschnittlicher Bestellwert:**

```dax
Ø Bestellwert = DIVIDE([Gesamtumsatz], [Gesamtmenge])
```

Beachten Sie, dass hier `DIVIDE` statt `/` steht. `DIVIDE` fängt Divisionen durch null sauber ab und liefert BLANK statt eines Fehlers — verwenden Sie es immer. Der Operator `/` wirft bei einem Nenner von null oder BLANK die Meldung „Division durch null nicht möglich" und reißt das gesamte Visual mit. Microsoft dokumentiert jeden Fall in der [DIVIDE-Referenz](https://learn.microsoft.com/de-de/dax/divide-function-dax).

**Gesamtkosten** (ein Measure mit einem Iterator):

```dax
Gesamtkosten = SUMX(Vertrieb, Vertrieb[Menge] * Vertrieb[Stückkosten])
```

`SUMX` ist ein Iterator: Er geht Zeile für Zeile durch die Tabelle, berechnet den Ausdruck und summiert anschließend die Ergebnisse. Iteratoren (`SUMX`, `AVERAGEX`, `MINX` und weitere) sind unverzichtbar, wenn vor der Aggregation auf Zeilenebene gerechnet werden muss. Die vollständige Syntax steht in der [SUMX-Referenz](https://learn.microsoft.com/de-de/dax/sumx-function-dax) von Microsoft.

Warum `Menge * Stückkosten` nicht als berechnete Spalte anlegen? Das wäre möglich — ändern sich die Stückkosten jedoch häufig, rechnet ein Measure bei jeder Aktualisierung neu, ohne das Modell aufzublähen. Bei großen Faktentabellen ist das Iterator-Muster speicherschonender.

**Bruttomarge in Prozent:**

```dax
Bruttomarge % =
DIVIDE(
    [Gesamtumsatz] - [Gesamtkosten],
    [Gesamtumsatz]
)
```

Formatieren Sie das Ergebnis im Menüband **Modellierung** als Prozentwert. Jedes Visual, das die Marge zeigt, respektiert nun die gesetzten Filter — nach Produkt, nach Region, nach Datum.

### Was passiert, wenn ein Anwender einen Datenschnitt anklickt

Wählt jemand im Kategorienschnitt „Elektronik" aus, passiert Folgendes:

1. Der Datenschnitt filtert `Produkte[Kategorie] = "Elektronik"`.
2. Der Filter fließt über die 1:n-Beziehung zur Tabelle `Vertrieb`.
3. `[Gesamtumsatz]` summiert nur noch die Zeilen, deren Produkt zur Kategorie Elektronik gehört.
4. `[Bruttomarge %]` rechnet mit den gefilterten Summen neu — ohne Änderung an der Formel.

Das ist die Stärke des Filterkontexts: **ein Measure, unendlich viele Sichten**.

## Die wichtigsten Funktionen für den Anfang

| Kategorie | Funktionen | Wozu Sie sie brauchen |
|----------|-----------|-------------------|
| Aggregation | `SUM`, `AVERAGE`, `MIN`, `MAX`, `COUNTROWS` | Das Fundament — jeder Bericht beginnt hier |
| Iteratoren | `SUMX`, `AVERAGEX`, `FILTER` | Rechnen auf Zeilenebene vor der Aggregation |
| Logik | `IF`, `SWITCH`, `COALESCE` | Bedingte Logik, vermeidet verschachtelte IFs |
| Filtersteuerung | `CALCULATE`, `ALL`, `ALLEXCEPT` | Den Filterkontext verändern — der Einstieg in fortgeschrittenes DAX |
| Zeitintelligenz | `TOTALYTD`, `SAMEPERIODLASTYEAR`, `DATEADD` | Berechnungen auf Datumsbasis |
| Fehlerbehandlung | `IFERROR`, `ISBLANK`, `COALESCE` | Sauberer Umgang mit fehlenden Daten |

Wenn Sie nur eine Funktion wirklich gründlich lernen, dann `CALCULATE` — sie ist der Schlüssel zu jedem fortgeschrittenen Muster. Die ausführliche Erklärung finden Sie in unserer [CALCULATE-Anleitung](/tutorials/calculate-function/).

## Drei typische Anfängerfehler (und ihre Lösung)

### 1. Eine Spalte referenzieren, wo ein Measure nötig ist

```dax
// Falsch — liefert den Spaltenbezug, keinen Wert
Gesamt = Vertrieb[Umsatz]

// Richtig
Gesamt = SUM(Vertrieb[Umsatz])
```

Ein reiner Spaltenbezug in einem Measure aggregiert nicht, sondern gibt zurück, was der aktuelle Zeilenkontext hergibt — in einem Visual ist das häufig BLANK. Umschließen Sie Spaltenbezüge immer mit einer Aggregationsfunktion.

### 2. Vergessen, dass Filter über Beziehungen fließen

Ein Datenschnitt auf `Produkte[Kategorie]` filtert `Vertrieb` nur, wenn die Beziehungsrichtung das zulässt. 1:n-Beziehungen filtern von der „Eins"-Seite (Dimension) zur „Viele"-Seite (Faktentabelle). Wenn Ihr Datenschnitt nicht wirkt:

- Öffnen Sie die Modellansicht und prüfen Sie die Richtung des Beziehungspfeils.
- Stellen Sie sicher, dass die Kardinalität `1:*` (1:n) ist und nicht `1:1` oder `*:*`.
- Prüfen Sie, ob die Verknüpfungsspalten zusammenpassende Werte enthalten und denselben Datentyp haben.

### 3. `IF` verwenden, obwohl `SWITCH` lesbarer ist

```dax
// Schwer lesbar — verschachtelte IFs werden ab drei Ebenen unübersichtlich
Klasse = IF(Vertrieb[Menge] < 10, "Klein", IF(Vertrieb[Menge] < 100, "Mittel", IF(Vertrieb[Menge] < 1000, "Groß", "Konzern")))

// Besser — SWITCH mit TRUE() ist flach und lesbar
Klasse =
SWITCH(
    TRUE(),
    Vertrieb[Menge] < 10, "Klein",
    Vertrieb[Menge] < 100, "Mittel",
    Vertrieb[Menge] < 1000, "Groß",
    "Konzern"
)
```

`SWITCH` ist außerdem etwas schneller als verschachtelte `IF`s, weil die Engine es als eine einzige Operation auswertet statt als Kette.

## DAX debuggen, wenn etwas schiefgeht

DAX-Fehlermeldungen sind notorisch wenig hilfreich. Ein Debugging-Ablauf, der funktioniert:

1. **Zuerst die Datentypen prüfen.** „Eine Tabelle mit mehreren Werten wurde geliefert" bedeutet fast immer, dass eine Zahlenspalte als Text gespeichert ist. Prüfen Sie die Datentypen in Power Query, bevor die Daten ins Modell geladen werden.

2. **DAX Studio verwenden.** Laden Sie DAX Studio (kostenlos) herunter und verbinden Sie es mit Ihrem Power-BI-Modell. Es zeigt die tatsächliche Abfrage, die Ihre Visuals erzeugen, erlaubt das Testen einzelner Measures und liefert Server-Timings, die verraten, welcher Teil Ihres DAX langsam ist.

3. **Komplexe Measures in Teile zerlegen.** Liefert ein Measure falsche Zahlen, legen Sie Zwischen-Measures an und prüfen Sie jedes einzeln:

```dax
// Statt alles auf einmal zu debuggen:
Marge % = DIVIDE(SUMX(Vertrieb, Vertrieb[Umsatz] - Vertrieb[Stückkosten] * Vertrieb[Menge]), SUM(Vertrieb[Umsatz]))

// In Schritten aufbauen:
_Schritt1 Kosten = SUMX(Vertrieb, Vertrieb[Stückkosten] * Vertrieb[Menge])
_Schritt2 Umsatz = SUM(Vertrieb[Umsatz])
_Schritt3 Marge = [_Schritt2 Umsatz] - [_Schritt1 Kosten]
Marge % = DIVIDE([_Schritt3 Marge], [_Schritt2 Umsatz])
```

Das Präfix `_` kennzeichnet diese Measures als intern — löschen Sie sie, sobald das endgültige Measure funktioniert.

4. **In einer Matrix testen, nicht auf einer Karte.** Eine Karte zeigt eine Zahl ohne Kontext. Eine nach einer Dimension gruppierte Matrix zeigt, ob das Measure je Zeile stimmt und ob die Gesamtsumme passt.

## Performance-Tipps für größere Modelle

- **Measures statt berechneter Spalten bevorzugen** — Measures rechnen bei Bedarf und vergrößern die Datei nicht.
- **`DIVIDE` statt `/` verwenden** — sicherer, und die Engine optimiert es.
- **Kein `FILTER` in `CALCULATE` für einfache Spaltenfilter** — `CALCULATE([Umsatz], Produkte[Farbe] = "Rot")` ist schneller als `CALCULATE([Umsatz], FILTER(Produkte, Produkte[Farbe] = "Rot"))`, weil die erste Variante direkt das Dictionary der Spalte nutzt.
- **Ungenutzte Spalten entfernen** — jede Spalte im Modell wird in den Speicher geladen, auch wenn kein Visual sie verwendet.

Die vollständige Vertiefung finden Sie in unserer Anleitung zur [Power BI Performance-Optimierung](/tutorials/de-power-bi-performance-optimization/).

## FAQ

**Sollte ich zuerst DAX oder Power Query lernen?**
Power Query zuerst — saubere Daten verhindern 80 Prozent der DAX-Probleme. Stimmen die Datentypen nicht oder ist das Modell schlecht strukturiert, rettet Sie kein DAX der Welt. Ein guter Einstieg ist unsere deutsche Anleitung [Power Query für Einsteiger](/tutorials/de-power-query-getting-started/).

**Ist DAX wie Excel-Formeln?**
Die Syntax sieht ähnlich aus, das Denkmodell ist aber ein völlig anderes. Excel-Formeln arbeiten auf Zellen, DAX auf gefilterten Tabellen. Wer DAX wie Excel schreibt, bekommt falsche Ergebnisse, die plausibel aussehen. Zwei Stunden in den Filterkontext investiert sparen Wochen beim Debuggen.

**Wie lange dauert es, DAX zu lernen?**
Die meisten Analysten schreiben schon nach einem Tag brauchbare Measures. Sicher im Umgang mit `CALCULATE`, Kontexttransition und Zeitintelligenz werden Sie nach zwei bis vier Wochen regelmäßiger Nutzung. Fortgeschrittene Muster wie Window Functions und Berechnungsgruppen brauchen drei bis sechs Monate.

**Kann ich ChatGPT oder Claude für DAX verwenden?**
Ja, aber prüfen Sie jede Formel. KI-Werkzeuge liefern häufig DAX, das „richtig aussieht", aber subtile Fehler in der Kontexttransition enthält. Die oben beschriebenen Debugging-Schritte helfen, solche Fehler zu finden. Testen Sie KI-generiertes DAX immer in DAX Studio, bevor Sie es produktiv einsetzen.

## Wie es weitergeht

Sie haben jetzt das Denkmodell: Measures rechnen im Filterkontext, berechnete Spalten im Zeilenkontext, und Iteratoren erlauben Rechnungen auf Zeilenebene vor der Aggregation. Der nächste Schritt ist das *Verändern* des Filterkontexts — genau das leistet `CALCULATE`.

Weiter geht es mit [CALCULATE: Die wichtigste DAX-Funktion](/tutorials/calculate-function/) und den [Mustern der Zeitintelligenz](/tutorials/time-intelligence/). Wenn Sie nicht weiterkommen, hilft unsere [DAX-Fehlerbehebung](/tutorials/dax-troubleshooting-guide/) bei den häufigsten Meldungen und ihren Lösungen. Die englische Originalfassung dieses Artikels finden Sie unter [DAX Basics](/tutorials/dax-basics/).

## Weiterführende Anleitungen

- [Bedingte Formatierung in Power BI](/tutorials/de-conditional-formatting-power-bi/) — wie Sie die Ergebnisse Ihrer Measures sofort lesbar machen.
- [Drillthrough in Power BI einrichten](/tutorials/de-power-bi-drill-through/) — vom Überblick zur Detailseite, ohne eine Zeile DAX.
- [DAX Basics (englische Originalfassung)](/tutorials/dax-basics/) — die englische Version dieses Artikels.
