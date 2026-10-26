---
title: "Power BI Performance-Optimierung: So beschleunigen Sie langsame Berichte"
description: "Langsame Power BI-Berichte frustrieren Nutzer und belasten das Modell. Diese Anleitung zeigt die häufigsten Ursachen für schlechte Performance und konkrete Maßnahmen — von der DAX-Optimierung bis zu schlanken Datenmodellen."
pubDate: 2026-10-12
updatedDate: 2026-10-12
category: "data-modeling"
difficulty: "Intermediate"
tags: ["performance", "optimierung", "dax", "datenmodell", "power-bi"]
author: Mireia
featured: false
---

Ein Power BI-Bericht, der mehrere Sekunden zum Laden braucht, ist ein Problem — nicht nur für die Nutzererfahrung, sondern auch für die Glaubwürdigkeit Ihrer Dashboards. In diesem Artikel erfahren Sie, wo Performance typischerweise verloren geht und wie Sie sie zurückgewinnen.

## Wo die Zeit bleibt

Die Ladezeit eines Berichts setzt sich aus drei Phasen zusammen:

1. **Abfrage (Query)** — Daten aus der Quelle holen (Power Query / M).
2. **Modell** — DAX-Berechnungen und das Speichermodell (VertiPaq) auswerten.
3. **Darstellung (Render)** — Visuals zeichnen und aktualisieren.

Die meisten echten Performance-Probleme liegen in Phase 1 oder 2, nicht beim Rendern.

## Schritt 1: Messen statt raten

Bevor Sie optimieren, messen Sie. Der **Performance Analyzer** (in Power BI Desktop unter dem Menü *Ansicht*) zeigt genau, wie lange jedes Visual und jede Abfrage braucht. Exportieren Sie das Ergebnis nach DAX Studio, um die zugrunde liegenden Abfragen zu analysieren.

Tipp: Sortieren Sie im Performance Analyzer nach Dauer. Das langsamste Visual ist Ihr erster Hebel.

## Schritt 2: Das Datenmodell verschlanken

Ein großes Modell ist ein langsames Modell. Die wirkungsvollsten Maßnahmen:

- **Nur benötigte Spalten laden.** Entfernen Sie Spalten, die niemand verwendet.
- **Richtige Datentypen.** Texte sind teurer als Ganzzahlen. Verwenden Sie nach Möglichkeit ganze Zahlen für Schlüssel.
- **Star-Schema statt Schneeflocke.** Denormalisieren Sie Dimensionen; Power BI arbeitet mit Stern-Schemas am schnellsten.
- **Query Folding nutzen.** Lassen Sie Filter und Transformationen von der Datenquelle erledigen, nicht von Power Query. Prüfen Sie in den angewandten Schritten, ob ein Schritt das Folding unterbricht.

## Schritt 3: DAX optimieren

Langsame Measures sind oft das Ergebnis von zeilenweisen Iterationen über große Tabellen.

```dax
// Langsam: jede Zeile einzeln gegen die gesamte Faktentabelle geprüft
Slow Sales :=
SUMX(
    Sales,
    IF(Sales[Amount] > 1000, Sales[Amount], 0)
)

// Schneller: Aggregation auf Datenbankebene, kein zeilenweiser IF
Fast Sales :=
CALCULATE(
    SUM(Sales[Amount]),
    Sales[Amount] > 1000
)
```

Regel: Vermeiden Sie `SUMX`/`FILTER` über Millionen von Zeilen, wenn ein `CALCULATE` mit Filter dasselbe leistet. `CALCULATE` nutzt die internen Speicherindexe (VertiPaq) viel besser aus.

## Schritt 4: VertiPaq verstehen

Power BI komprimiert Daten spaltenweise. Hohe Kardinalität — also viele einzigartige Werte in einer Spalte — verschlechtert die Kompressionsrate. Vermeiden Sie daher:

- Eindeutige IDs als Text (verwenden Sie Ganzzahlen).
- Datumszeitstempel mit Uhrzeit in Faktentabellen (trennen Sie Datum und Uhrzeit).
- Frei erfassbare Textfelder als Schlüssel.

Das kostenlose Tool **VertiPaq Analyzer** zeigt die Spalten mit der schlechtesten Kompressionsrate — ein hervorragender Ausgangspunkt.

## Häufige Fehler

1. **Zu viele Visuals auf einer Seite.** Jedes Visual ist eine eigene Abfrage. Weniger Visuals, mehr Geschwindigkeit.
2. **`CALCULATE` in einer schleifenartigen `SUMX`-Struktur.** Das vervielfacht die Rechenzeit.
3. **Importmodus, wo DirectQuery nötig wäre (oder umgekehrt).** Import ist meist schneller; DirectQuery nur, wenn Echtzeit-Pflicht besteht.

## Weiterführende Anleitungen

- [Bedingte Formatierung in Power BI](/tutorials/conditional-formatting-power-bi/) — die englische Anleitung zu Visual-Features.
- [Star-Schema in Power BI](/tutorials/data-modeling-star-schema/) — die Grundlage schneller Modelle.
- [DAX-Optimierung in Power BI](/tutorials/power-bi-dax-optimization/) — Measures beschleunigen.

## Related Reading

- [Incremental Refresh in Power BI: Setup and Gotchas](/tutorials/power-bi-incremental-refresh/)

- [VertiPaq Analyzer: Optimize Your Power BI Data Model](/tutorials/vertipaq-optimizer-power-bi/)