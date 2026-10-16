---
title: "Power Query für Einsteiger: Daten in Power BI vorbereiten"
description: "Power Query ist der ETL-Editor von Power BI — hier bereiten Sie Daten vor, bevor sie ins Modell gelangen. Diese Einsteigeranleitung zeigt den Power Query Editor, die wichtigsten Transformationen und warum『Query Folding』wichtig ist."
pubDate: 2026-10-12
updatedDate: 2026-10-12
category: "power-query"
difficulty: "Beginner"
tags: ["power-query", "einstieg", "etl", "transformation", "m-language"]
author: Mireia
featured: false
---

Bevor Daten in einem Power BI-Modell landen, werden sie meist bereinigt und umgeformt. Genau dafür ist **Power Query** da — der integrierte ETL-Editor (Extract, Transform, Load). Dieser Artikel ist der Einstieg.

## Der Power Query Editor

Öffnen Sie den Editor über **Start → Daten transformieren**. Sie sehen drei Bereiche:

1. **Abfragen** (links) — Ihre Datenquellen und Schritte.
2. **Vorschau** (mitte) — die Tabelle mit dem Ergebnis.
3. **Angewandte Schritte** (rechts) — jede Transformation als eigener, rückgängig machbarer Schritt.

Jeder Schritt ist reproduzierbar: Beim Aktualisieren der Daten läuft Power Query die Schritte in der gleichen Reihenfolge erneut durch.

## Die häufigsten Transformationen

- **Datentyp festlegen** — Zahl, Text, Datum. Immer explizit setzen, sonst rechnet Power BI falsch.
- **Spalten entfernen** — schlanke Modelle sind schnelle Modelle.
- **Filtern** — Zeilen ausschließen, die Sie nicht brauchen.
- **Spalte hinzufügen** — berechnete Spalten, z. B. eine Bedingung (siehe unten).
- **Zusammenführen (Merge)** — wie `VLOOKUP`, verknüpft zwei Tabellen über einen Schlüssel.
- **Anhängen (Append)** — fügt mehrere gleich strukturierte Dateien zu einer Tabelle zusammen.

## Bedingte Spalten ohne Code

Mit **Spalte hinzufügen → Bedingte Spalte** bauen Sie If-Dann-Sonst-Logik visuell:

| Wenn | Dann |
|---|---|
| `[Umsatz]` `ist größer als` `10000` | `"Groß"` |
| Sonst | `"Klein"` |

Für komplexere Logik (UND/ODER, dynamische Werte) wechseln Sie zu **Benutzerdefinierte Spalte** und schreiben M-Code:

```powerquery
= if [Umsatz] > 10000 then "Groß" else "Klein"
```

## Query Folding — der Geschwindigkeitstrick

Power Query kann Filter und Transformationen an die *Datenquelle* weiterreichen (z. B. an SQL Server), statt Millionen von Zeilen lokal zu laden. Das nennt man **Query Folding**. Solange ein Schritt das Folding nicht unterbricht, arbeitet die Datenbank für Sie.

Achtung: Manche Schritte brechen das Folding — etwa bestimmte benutzerdefinierte Spalten oder das Mischen von Datenquellen. Prüfen Sie die „angewandten Schritte" auf Warnsymbole.

## Nächste Schritte

- [Bedingte Formatierung in Power BI](/tutorials/de-conditional-formatting-power-bi/) — verwandte deutsche Anleitung.
- [Power BI Performance-Optimierung](/tutorials/de-power-bi-performance-optimization/) — warum schlanke Abfragen zählen.
- [Power BI Tutorials (Englisch)](/tutorials/) — das vollständige englische Verzeichnis.
