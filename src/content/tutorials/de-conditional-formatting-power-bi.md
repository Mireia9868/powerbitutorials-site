---
title: "Bedingte Formatierung in Power BI: Eine komplette Anleitung"
description: "Mit bedingter Formatierung in Power BI werden Tabellen und Diagramme sofort lesbar — rot bei Zielverfehlung, grün bei Übererfüllung. Diese Anleitung erklärt Regeln, Farbverläufe und die wiederverwendbare Measure-Methode."
pubDate: 2026-10-12
updatedDate: 2026-10-12
category: "visualization"
difficulty: "Beginner"
tags: ["conditional-formatting", "bedingte-formatierung", "visualization", "farben", "power-bi"]
author: Mireia
featured: false
---

Bedingte Formatierung verwandelt eine flache Tabelle in einen Bericht, der sich von selbst abliest. Rote Werte, wenn ein Ziel verfehlt wird, grüne, wenn es übertroffen ist, ein Farbverlauf, der den Trend zeigt — all das ist in Power BI integriert.

## Die vier Methoden zur Farbsteuerung

| Methode | Am besten für | Eingabestelle |
|---|---|---|
| **Regeln** (Farbe nach Wert) | Einfache Schwellenwerte | Visual → Feld → **Bedingte Formatierung → Hintergrundfarbe** |
| **Feldwert** (eine Measure) | Logik, die überall gleich bleibt | Gleiches Menü → **Formatieren nach → Feldwert** |
| **Farbverlauf** | Stärke zeigen, nicht nur Bestehen/Nicht bestehen | Gleiches Menü → **Formatieren nach → Verlauf** |
| **Symbole / Datenbalken** | Status auf einen Blick in Tabellen | Gleiches Menü → **Symbole** oder **Datenbalken** |

Die wichtigste Regel: **Bevorzugen Sie eine Measure gegenüber händisch gebauten Regeln.** Eine Farb-Measure (Feldwert) wird einmal definiert und von jedem Visual wiederverwendet. Händisch gebaute Regeln werden pro Visual neu erstellt und driften auseinander, sobald Sie einen Schwellenwert ändern.

## Farbe nach Regeln (die Grundlagen)

Klicken Sie mit der rechten Maustaste auf ein Feld in einer Tabelle oder Matrix → **Bedingte Formatierung → Hintergrundfarbe**, dann wählen Sie **Formatieren nach → Regeln**. Sie legen Bedingungen fest wie „wenn Umsatz < 1000 dann rot, sonst grün". Das ist ideal für ein einzelnes Visual.

```dax
// Die Measure-Variante einer Regel — einmal definieren, überall wiederverwenden
CF Umsatz vs Ziel :=
VAR Pct = DIVIDE([Gesamtumsatz], [Umsatzziel], 0)
RETURN
    SWITCH(TRUE(),
        Pct > 1.05, "#22C55E",
        Pct >= 0.95, "#F59E0B",
        "#EF4444")
```

Wenden Sie sie mit **Formatieren nach → Feldwert** an und wählen Sie `CF Umsatz vs Ziel`. Jedes Visual, das diese Measure nutzt, zeigt dieselbe Logik — und bei einer Änderung der Schwellenwerte aktualisieren sich alle auf einmal.

## Farbverläufe und Datenbalken

Für zusammenhängende Werte zeigt ein Verlauf (niedrig → hoch) die Rangfolge besser als eine rot/grün-Aufteilung. Datenbalken zeichnen einen Mini-Balken in die Zelle — ideal, um Werte innerhalb einer Spalte zu vergleichen, ohne mehr Platz zu beanspruchen.

## Bedingte Formatierung auf Diagrammen

Diagramme werden anders formatiert als Tabellen — Sie färben die *Datenpunkte*, nicht die Zellen:

- **Balken-/Säulendiagramme** — färben nach einer Measure oder nach Regeln auf dem Wert.
- **Liniendiagramme** — Marker oder Linie nach Feldwert formatieren.
- **Gauges** — Bogen- und Zielwertfarben festlegen.
- **Karten / KPIs** — die eingebaute Status-Option oder die Hintergrundfarbe nutzen.

## Häufige Fehler

1. **Dieselbe Regel in zehn Visualen händisch bauen.** Sie laufen auseinander. Nutzen Sie eine Measure.
2. **Zu erwarten, dass der Format-Pinsel bedingte Formatierung kopiert.** Er kopiert Stile, nicht Regeln.
3. **„Conflicting metrics"-Fehler.** Wenn zwei Formatregeln dasselbe Feld mit überlappenden Bedingungen treffen, meldet Power BI einen Konflikt. Lösen Sie ihn, indem Sie die Logik in einer einzigen Measure bündeln.

## Praxisbeispiel: eine Vertriebs-Tabelle mit Ampel-Logik

Nehmen wir ein konkretes Szenario. Eine Tabelle zeigt Umsatz, Ziel und Erfüllungsgrad pro Vertriebsmitarbeiter. Sie möchten dreierlei erreichen: eine Ampel (rot/gelb/grün), Datenbalken für den Umsatz und einen Farbverlauf für den Erfüllungsgrad. Gehen Sie so vor:

1. **Erfüllungsgrad als Measure** anlegen — `DIVIDE([Gesamtumsatz], [Umsatzziel])`.
2. **Ampel über eine Farb-Measure** steuern — die `CF Umsatz vs Ziel` von oben liefert hexadezimale Farben. Binden Sie sie an **Zellen → Hintergrundfarbe → Formatieren nach → Feldwert**.
3. **Datenbalken** auf die Spalte `[Gesamtumsatz]` legen: Rechtsklick auf die Spalte → **Bedingte Formatierung → Datenbalken**. Die Balkenlänge passt sich automatisch an den Maximalwert an.
4. **Farbverlauf** auf den Erfüllungsgrad: **Formatieren nach → Verlauf**, Minimum rot, Maximum grün, Mittelpunkt bei 100 %.

Das Ergebnis ist in einem Blick lesbar: Wer unter 95 % liegt, sieht Rot; die Balken zeigen die absolute Größenordnung; der Verlauf macht Zwischenstufen sichtbar. Wichtig: Alle drei Formatierungen nutzen dieselben Measures. Ändern Sie später den Schwellenwert von 95 % auf 90 %, genügt eine Änderung in `CF Umsatz vs Ziel` — alle Visuals folgen automatisch. Genau das ist der Vorteil der Measure-Methode gegenüber händisch gebauten Regeln.

## Farben konsistent halten

Ein häufig unterschätztes Problem: Wenn jedes Visual seine eigenen Farben definiert, sieht ein Bericht nach zehn Minuten Basteln aus wie ein Flickenteppich. Drei Gewohnheiten verhindern das:

- **Ein zentrales Farb-Measure pro Logik.** NICHT „Umsatz grün" in Visual A und „Umsatz grün" mit leicht anderem Hexwert in Visual B.
- **Hexwerte statt Farbnamen.** `"#22C55E"` ist eindeutig; `"Grün"` wird je nach Theme anders interpretiert. Notieren Sie sich die vier oder fünf Farben Ihres Berichts an einer Stelle (etwa in einer kleinen Measure-Tabelle).
- **Farben nicht allein als Informationsträger.** Etwa 8 % der Männer haben eine Farbfehlsichtigkeit. Kombinieren Sie Rot/Grün immer mit einem Symbol (▲/▼) oder einer Zahl, damit die Aussage auch ohne Farbwahrnehmung verständlich bleibt.

## Bedingte Formatierung und Performance

Farb-Measures werden für **jede Zelle** ausgewertet. Bei einer Matrix mit 5.000 Zellen und einem komplexen `CF`-Measure kann das spürbar werden. Drei Regeln halten es schnell:

1. Nutzen Sie `VAR`, um einen Wert einmal zu berechnen statt ihn mehrfach in `SWITCH` zu wiederholen — das gilt auch in Farb-Measures.
2. Vermeiden Sie Iteratoren (`SUMX`, `FILTER`) über die Faktentabelle innerhalb einer Farb-Measure. Lesen Sie eine einfache Measure wie `[Erfüllungsgrad]` aus.
3. Prüfen Sie im **Performance Analyzer**, ob das langsamste Visual eines mit bedingter Formatierung ist. Wenn ja, vereinfachen Sie zuerst die Farb-Logik, bevor Sie am Modell schrauben.

Weiterführend: [DAX-Variablen (Englisch)](/tutorials/dax-variables-guide/) erklärt `VAR` im Detail, und [Power BI Performance-Optimierung](/tutorials/de-power-bi-performance-optimization/) zeigt die systematische Fehlersuche.

## Häufige Fehler

1. **Dieselbe Regel in zehn Visualen händisch bauen.** Sie laufen auseinander. Nutzen Sie eine Measure.
2. **Zu erwarten, dass der Format-Pinsel bedingte Formatierung kopiert.** Er kopiert Stile, nicht Regeln.
3. **„Conflicting metrics"-Fehler.** Wenn zwei Formatregeln dasselbe Feld mit überlappenden Bedingungen treffen, meldet Power BI einen Konflikt. Lösen Sie ihn, indem Sie die Logik in einer einzigen Measure bündeln.
4. **Farb-Measure gibt Text statt Hex zurück.** Wenn die Measure einen Wert wie `"rot"` liefert, bleibt die Zelle weiß. Nur gültige Hex-Codes (`#RRGGBB`) werden als Farbe erkannt.
5. **Verlauf greift nicht auf Diagrammen.** Bei Linien- und Balkendiagrammen formatieren Sie die Datenpunkte, nicht die Zellen — das Menü heißt dort anders (siehe Abschnitt „Bedingte Formatierung auf Diagrammen").

## Vergleich: Regeln, Feldwert oder Verlauf — was wann?

Die drei Mechanismen schließen sich nicht aus, aber sie lösen unterschiedliche Aufgaben. Diese Entscheidungshilfe spart Ausprobieren:

| Situation | Richtige Wahl | Warum |
|---|---|---|
| Ein Visual, ein fester Schwellenwert, nie wieder angefasst | **Regeln** | Am schnellsten eingerichtet, kein Measure nötig |
| Gleiche Logik in mehreren Visuals | **Feldwert (Measure)** | An einer Stelle ändern, überall wirksam |
| Stärke oder Rangfolge sichtbar machen | **Verlauf** | Zeigt Zwischenstufen, nicht nur Bestehen/Nicht bestehen |
| Status in einer Tabelle auf einen Blick | **Symbole / Datenbalken** | Kompakt und ohne zusätzliche Spalte |
| Logik hängt von einem slicer-gewählten Ziel ab | **Feldwert (Measure)** | Nur Measures reagieren auf Filterkontext |

Die Faustregel: Sobald Sie dieselbe Bedingung ein zweites Mal bauen würden, hören Sie auf zu klicken und schreiben eine Measure. Was wie ein kleiner Zeitaufwand wirkt, erspart Ihnen Stunden der Nacharbeit, wenn sich Schwellenwerte ändern.

## FAQ: Häufige Fragen zur bedingten Formatierung

**F: Warum zeigt meine Measure-Farbe keine Wirkung?**
A: Prüfen Sie drei Dinge: Liefert die Measure einen gültigen Hex-Code (mit `#`)? Ist sie unter **Formatieren nach → Feldwert** ausgewählt? Und greift sie auf die richtige Eigenschaft (Hintergrund vs. Schriftfarbe)?

**F: Kann ich eine Zelle gleichzeitig nach Wert UND nach Text formatieren?**
A: Über eine Measure ja — bauen Sie die gewünschte Logik mit `SWITCH(TRUE(), …)` und mehreren Bedingungen. Händische Regeln stoßen hier schnell an ihre Grenzen.

**F: Werden Farbregeln beim Export nach PDF/Excel übernommen?**
A: In der Regel ja, aber nicht immer identisch — exportierte Farben können je nach Zielformat abweichen. Prüfen Sie den Export vor dem Verteilen.

**F: Wie setze ich einen Schwellenwert zurück, der auf ein Datum basiert?**
A: Nutzen Sie eine Measure mit `TODAY()` oder `SELECTEDVALUE` aus einer Parameters-Tabelle statt eines festen Werts. So bleibt die Ampel bei jedem Öffnen aktuell.

## Weiterführende Anleitungen

- [Bedingte Formatierung auf Diagrammen (Englisch)](/tutorials/conditional-formatting-charts-power-bi/) — Linien, Balken und Gauges im Detail.
- [Formatierung basierend auf einer Measure (Englisch)](/tutorials/conditional-formatting-based-on-measure/) — die Measure-Methode ausführlich.
- [Power BI Performance-Optimierung](/tutorials/de-power-bi-performance-optimization/) — verwandte deutsche Anleitung.
- [Power BI Tutorials (Englisch)](/tutorials/) — das vollständige englische Verzeichnis.
