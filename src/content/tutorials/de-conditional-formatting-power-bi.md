---
title: "Bedingte Formatierung in Power BI: Eine komplette Anleitung"
description: "Mit bedingter Formatierung in Power BI werden Tabellen und Diagramme sofort lesbar — rot bei Zielverfehlung, grün bei Übererfüllung. Diese Anleitung erklärt Regeln, Farbverläufe und die wiederverwendbare Measure-Methode."
pubDate: 2026-10-12
updatedDate: 2026-10-12
category: "visualization"
difficulty: "Beginner"
tags: ["conditional-formatting", "bedingte-formatierung", "visualization", "farben", "power-bi"]
author: "Power BI Tutorials Team"
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
        Pct > 1,05, "#22C55E",
        Pct >= 0,95, "#F59E0B",
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

## Weiterführende Anleitungen

- [Power BI Performance-Optimierung](/tutorials/de-power-bi-performance-optimization/) — verwandte deutsche Anleitung.
- [Power BI Tutorials (Englisch)](/tutorials/) — das vollständige englische Verzeichnis.
