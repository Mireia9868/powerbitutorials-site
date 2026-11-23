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

## Datenquellen verbinden: Excel, CSV, Ordner und Datenbanken

Bevor Sie transformieren, müssen Sie eine Quelle auswählen. **Start → Daten abrufen** bietet die gängigen Optionen, die für Einsteiger am wichtigsten sind:

- **Excel-Arbeitsmappe (.xlsx):** Wählen Sie die Datei und dann im Navigator das gewünschte Blatt oder die Tabelle. Achten Sie darauf, dass Ihre Daten eine Kopfzeile haben — Power Query übernimmt sie automatisch als Spaltennamen.
- **CSV / Text:** Hier ist die richtige **Codierung** entscheidend. Deutsche CSV-Dateien sind oft in `Windows-1252` oder `UTF-8` gespeichert; eine falsche Wahl produces verstümmelte Umlaute („MÃ¼nchen" statt „München"). Stellen Sie außerdem das **Trennzeichen** ein (Semikolon ist in Deutschland üblich, Komma international) und prüfen Sie, ob das **Gebietsschema** zu Ihren Zahlen passt — „1.234,56" und „1,234.56" bedeuten etwas anderes.
- **Ordner:** Wenn monatliche Dateien im selben Format vorliegen (`Umsatz_01.xlsx`, `Umsatz_02.xlsx` …), wählen Sie **Aus Ordner**. Power Query erstellt eine Dateiliste, die Sie mit **Anhängen** zu einer Tabelle zusammenführen. Neue Monatsdateien werden beim Aktualisieren automatisch übernommen — das ersetzt manuelle Copy-Paste-Arbeit dauerhaft.
- **SQL-Datenbank / SQL Server:** Hier glänzt Query Folding (siehe unten). Sie geben Server und Datenbank an und wählen die Tabelle oder schreiben eine Abfrage.

Ein praktischer Tipp für den Einstieg: Beginnen Sie mit einer kleinen Datei (ein paar hundert Zeilen), bis Sie die Schritte verstehen. Große Quellen machen das Ausprobieren langsamer, ohne dass Sie mehr lernen.

## Die M-Sprache: was hinter den Klicks passiert

Jeder Klick im Editor erzeugt eine Zeile Code in der **M-Sprache** (offiziell: Power Query Formula Language). Sie müssen kein Programmierer sein, aber wenn Sie den Code lesen können, verstehen Sie, was Power BI wirklich tut — und Sie können Schritte korrigieren, die die Oberfläche nicht anbietet.

Klicken Sie im Menü **Ansicht → Erweiterter Editor**, um den Code einer Abfrage zu sehen. Das Grundgerüst ist immer gleich:

```powerquery
let
    Quelle = Csv.Document(File.Contents("C:\Daten\umsatz.csv"), [Encoding=65001]),
    Kopfzeilen = Table.PromoteHeaders(Quelle),
    Typen = Table.TransformColumnTypes(Kopfzeilen, {{"Umsatz", type number}}),
    Gefiltert = Table.SelectRows(Typen, each [Umsatz] > 0)
in
    Gefiltert
```

Zwei Dinge fallen auf: Jede Zeile definiert ein Zwischenergebnis mit einem Namen (`Quelle`, `Kopfzeilen` …), und die letzte Zeile nach `in` bestimmt, was zurückgegeben wird. Die Namen entsprechen exakt den Einträgen unter **Angewandte Schritte**. Wenn Sie einen Schritt löschen, entfernen Sie seine Zeile — abhängige Schritte darunter müssen dann natürlich angepasst werden.

Die Funktion `each` ist eine Kurzform für „für die aktuelle Zeile". `Table.SelectRows(Typen, each [Umsatz] > 0)` bedeutet also: behalte nur Zeilen, in denen der Umsatz größer als null ist. Sobald Sie dieses Muster verstehen, können Sie die meisten Filter selbst schreiben.

## Abfragen organisieren: Gruppen, Parameter und Referenzen

Mit wachsenden Projekten werden viele einzelne Abfragen unübersichtlich. Drei Werkzeuge helfen:

1. **Gruppen:** Rechtsklick auf eine Abfrage → **In Gruppe verschieben**. So trennen Sie etwa „Quellen", „Transformationen" und „Ausgaben" visuell im Abfragenbereich.
2. **Parameter:** Unter **Start → Parameter verwalten** legen Sie Werte an, die Sie mehrfach brauchen — etwa einen Pfad oder ein Schwellenjahr. Statt den Pfad in jeder Abfrage fest zu verdrahten, verwenden Sie den Parameter. Beim Umzug auf einen anderen Rechner ändern Sie ihn an einer Stelle.
3. **Referenzabfragen:** Rechtsklick → **Referenz** erstellt eine neue Abfrage, die auf dem Ergebnis einer bestehenden aufbaut. Das ist der saubere Weg, wenn aus einer Rohdatei mehrere Ausgangstabellen entstehen (z. B. eine Umsatz- und eine Kundenansicht). Änderungen an der Quelle wirken auf alle Ableitungen — anders als beim Kopieren, wo Sie jede Kopie einzeln pflegen müssten.

Deaktivieren Sie außerdem das **Laden** von Zwischenabfragen: Rechtsklick → **Laden in Data Model deaktivieren**. Sonst landen Hilfstabellen, die niemand braucht, im Modell und blähen es auf.

## Häufige Fehler und ihre Ursachen

| Symptom | Wahrscheinliche Ursache | Lösung |
|---|---|---|
| Umlaute werden falsch angezeigt | Falsche Codierung beim CSV-Import | Encoding auf `UTF-8` (65001) oder `Windows-1252` setzen |
| Zahlen werden als Text erkannt | Gebietsschema passt nicht zum Trennzeichen | Gebietsschema in der Quelle auf „Deutsch" stellen |
| Spalte verschwindet nach Aktualisierung | Quelldatei hat eine andere Spaltenreihenfolge | Spalten nach Namen referenzieren, nicht nach Position |
| „Spalte nicht gefunden"-Fehler | Zwischenschritt umbenannt oder gelöscht | Angewandte Schritte prüfen, abhängige Zeilen im M-Code anpassen |
| Aktualisierung ist sehr langsam | Query Folding wurde unterbrochen | Warnsymbole bei den Schritten suchen (siehe oben) |
| Modell ist unnötig groß | Hilfsabfragen werden geladen | „Laden in Data Model deaktivieren" für Zwischenschritte |

Ein weiterer Klassiker: Wenn Sie eine Spalte mit gemischten Werten (Zahlen *und* Text wie „k. A.") importieren, erkennt Power Query die Spalte oft als Text, und Summen funktionieren nicht. Filtern Sie die Ausreißer vor dem Typwechsel heraus oder ersetzen Sie sie durch `null`.

## FAQ: Häufige Fragen zu Power Query für Einsteiger

**F: Muss ich M-Code lernen, um Power Query zu nutzen?**
A: Nein. Über 90 % der alltäglichen Aufgaben lösen Sie über die Menüs. Der Code wird erst interessant, wenn Sie präzise filtern oder Fehler in automatisch erzeugten Schritten korrigieren wollen.

**F: Werden meine Schritte bei jeder Aktualisierung wiederholt?**
A: Ja, in der gleichen Reihenfolge. Genau das macht Power Query reproduzierbar: Ein neuer Monat wird identisch verarbeitet wie der davor.

**F: Was ist der Unterschied zwischen „Spalte hinzufügen" und einer berechneten Spalte in DAX?**
A: Eine Spalte in Power Query wird beim Laden berechnet und physisch im Modell gespeichert. Eine DAX-berechnete Spalte wird ebenfalls gespeichert, aber im Modell berechnet. Beide erhöhen die Dateigröße — eine Measure hingegen nicht. Für zeilenweise Bereinigung ist Power Query die richtige Wahl.

**F: Kann ich mehrere Dateien mit unterschiedlichen Spalten kombinieren?**
A: Ja, aber **Aus Ordner** verlangt identische Spaltennamen. Weichen sie ab, müssen Sie die Spalten vor dem Anhängen angleichen — sonst entstehen leere Felder.

**F: Warum wird meine Abfrage nicht aktualisiert, obwohl die Datei neue Zeilen hat?**
A: Prüfen Sie zuerst den Dateipfad und dann, ob die Abfrage in den Data Model geladen wird. Bei Ordnerabfragen stellen Sie sicher, dass neue Dateien denselben Namensaufbau und dasselbe Format haben.

## Nächste Schritte

- [Bedingte Formatierung in Power BI](/tutorials/de-conditional-formatting-power-bi/) — verwandte deutsche Anleitung.
- [Power BI Performance-Optimierung](/tutorials/de-power-bi-performance-optimization/) — warum schlanke Abfragen zählen.
- [Merge-Abfragen (Englisch)](/tutorials/power-query-merge-queries/) — Tabellen über einen Schlüssel verknüpfen.
- [Anhängen von Abfragen (Englisch)](/tutorials/power-query-append-queries/) — mehrere Tabellen stapeln.
- [Power BI Tutorials (Englisch)](/tutorials/) — das vollständige englische Verzeichnis.
