---
title: "DirectQuery vs. Import: Speichermodus in Power BI richtig wählen"
description: "Import, DirectQuery, Dual oder Direct Lake — vier Speichermodi, eine Entscheidung. Wann welcher Modus passt, mit Vergleichsmatrix zu Geschwindigkeit, Kosten und Datenaktualität sowie den Fehlern, die schnelle Berichte ausbremsen."
pubDate: 2026-11-23
updatedDate: 2026-11-23
category: "data-modeling"
difficulty: "Advanced"
tags: ["directquery", "importmodus", "speichermodus", "datenmodellierung", "performance", "direct-lake"]
author: Mireia
featured: false
draft: false
---

Jedes Power BI-Semantic-Model bekommt einen Speichermodus. Er entscheidet, woher die Daten kommen, wenn jemand auf ein Visual klickt: aus dem speicherinternen Modell, direkt aus der Quelldatenbank oder aus einer Mischung von beidem. Die Wahl zwischen **Import** und **DirectQuery** verändert nicht nur die Abfragegeschwindigkeit, sondern auch, wie frisch die Daten sind, wie stark die Quelle belastet wird und welche DAX-Funktionen überhaupt zur Verfügung stehen.

Diese Anleitung vergleicht die vier Modi, zeigt die Entscheidungskriterien, erklärt das Hybridmodell mit Aggregationen und benennt die Fehler, die aus einem schnellen Bericht ein Geduldsspiel machen. Das Beispiel durchzieht ein Maschinenbauer aus Stuttgart mit 40 Mio. € Jahresumsatz, dessen Vertriebsbericht jeden Morgen um 7:00 Uhr aktuell sein muss.

## Die vier Speichermodi

### Import

Beim Import kopiert Power BI die Daten beim Aktualisieren in die speicherinterne Engine (VertiPaq). Jede spätere Abfrage läuft gegen diese Kopie.

**So funktioniert es:**

1. Sie verbinden sich mit einer Quelle und wählen die Tabellen aus.
2. Power BI lädt die Zeilen in die spaltenorientierte VertiPaq-Datenbank.
3. Alle DAX-Abfragen laufen gegen die Kopie im Arbeitsspeicher.
4. Neue Daten kommen erst mit der nächsten Aktualisierung hinzu — geplant oder manuell.

**Vorteile:**

- Die schnellste Abfrageleistung, für die meisten Visuals deutlich unter einer Sekunde
- Der volle DAX-Funktionsumfang
- Funktioniert nach der ersten Aktualisierung auch ohne Verbindung zur Quelle
- Alle Power BI-Funktionen stehen zur Verfügung, inklusive Q&A und Schnelleinblicken
- Aggregationen und berechnete Tabellen ohne Einschränkung

**Nachteile:**

- Die Daten sind so alt wie die letzte Aktualisierung
- Die Modellgröße ist durch die Kapazität begrenzt (1 GB bei Pro, 100 GB bei P1)
- Die Aktualisierungsdauer wächst mit dem Datenvolumen
- Große Modelle verursachen laufende Kosten für die Kapazität

**Wann Import passt:** Wenn das Volumen in den Arbeitsspeicher passt und niemand Daten in Echtzeit braucht. Für die meisten Berichte ist das die richtige Wahl — auch für den Stuttgarter Vertriebsbericht, solange eine nächtliche Aktualisierung genügt.

### DirectQuery

DirectQuery speichert keine Daten. Bei jeder Interaktion mit einem Visual übersetzt Power BI die Anfrage in SQL und schickt sie an die Quelldatenbank.

**So funktioniert es:**

1. Sie verbinden sich mit einer unterstützten Quelle wie SQL Server, Snowflake oder Oracle.
2. Power BI speichert nur Metadaten und Beziehungen.
3. Jede Filteränderung erzeugt eine native SQL-Abfrage.
4. Die Quelldatenbank führt sie aus und liefert das Ergebnis zurück.

**Vorteile:**

- Daten in Echtzeit, ohne Aktualisierungsverzögerung
- Keine Datenkopie im Power BI-Dienst — relevant für Compliance und Datenschutz
- Datenmengen jenseits der Speichergrenze bleiben nutzbar
- Eine einzige Datenquelle, damit keine Abweichungen zwischen Kopie und Original

**Nachteile:**

- Die Geschwindigkeit hängt vollständig von der Quelldatenbank ab
- Nicht alle DAX-Funktionen werden unterstützt, besonders bei Zeitintelligenz und Statistik
- Berechnete Tabellen sind nicht möglich
- Viele gleichzeitige Nutzer können die Quelle überlasten
- Einige Funktionen wie Q&A fehlen

**Wann DirectQuery passt:** Wenn Aktualität wichtiger ist als Tempo, wenn das Volumen den Arbeitsspeicher sprengt oder wenn Richtlinien den Export der Daten verbieten.

### Dual

Dual speichert eine Tabelle im Arbeitsspeicher und kann trotzdem per DirectQuery auf die Quelle zugreifen, wenn es nötig wird. In einem Hybridmodell ist Dual die Brücke: Dimensionstabellen bleiben im Speicher, Faktentabellen laufen über DirectQuery, und Beziehungen zwischen beiden funktionieren ohne Bruch.

**Typischer Einsatz:** Die Dimensionstabellen eines Sternschemas, während die Faktentabelle per DirectQuery angebunden ist. Wer die Struktur noch einmal nachlesen will, findet sie in der Anleitung zum [Sternschema](/tutorials/data-modeling-star-schema/).

### Direct Lake

Direct Lake kam mit Microsoft Fabric und liest Delta-Tabellen direkt aus OneLake — ohne Import und ohne SQL-Umweg wie bei DirectQuery. Es ist der einzige Modus, der Import-Geschwindigkeit ohne Aktualisierungsplan bietet.

**So funktioniert es:**

1. Die Daten liegen bereits als Delta-Parquet in OneLake, meist in einem Lakehouse oder Warehouse.
2. Ein semantisches Modell zeigt auf diese Tabellen.
3. Bei der ersten Abfrage lädt Power BI die benötigten Spalten in den Speicher — Fabric nennt das *Framing*.
4. Danach laufen Abfragen gegen diese Daten, bis neue Delta-Commits sie ungültig machen.

**Vorteile:**

- Abfragen fast auf Import-Niveau, ohne Aktualisierungsplan
- Keine zweite Datenkopie, also nichts, was synchron gehalten werden muss
- Keine SQL-Last pro Visual auf einem Quellsystem
- Neue Zeilen sind sichtbar, sobald die Delta-Tabelle aktualisiert wurde

**Nachteile:**

- Erfordert eine Fabric-Kapazität. Mit Power BI Pro allein ist der Modus nicht verfügbar — das ist eine Beschaffungsentscheidung, keine Modellierungsfrage
- Die Daten müssen bereits als Delta in OneLake liegen; ein Connector ist Direct Lake nicht
- Manche DAX-Abfragen lassen sich nicht aus den geladenen Spalten beantworten und fallen entweder auf DirectQuery zurück oder schlagen fehl
- Die Governance unterscheidet sich vom Import: Spaltensicherheit auf Zeilenebene und einige Lineage-Funktionen verhalten sich anders

**Wann Direct Lake passt:** Wenn Sie auf Fabric sind, die Daten in OneLake landen und Import-Tempo ohne eigene Aktualisierungspipeline wollen.

## Vergleichsmatrix

| Kriterium | Import | DirectQuery | Dual | Direct Lake |
|---|---|---|---|---|
| Abfragegeschwindigkeit | ⚡ Am schnellsten | 🐌 Abhängig von der Quelle | ⚡ Schnell als Brücke | ⚡ Nahe Import |
| Datenaktualität | Stand der letzten Aktualisierung | Echtzeit | Gemischt | Stand der Delta-Tabelle |
| Maximale Datenmenge | Speicherbegrenzt | Quellenbegrenzt | Speicherbegrenzt | Kapazitätsbegrenzt |
| DAX-Unterstützung | Vollständig | Teilweise | Vollständig | Teilweise (Fallback) |
| Last auf der Quelldatenbank | Gering, nur bei Aktualisierung | Hoch, bei jeder Abfrage | Mittel | Keine |
| Voraussetzung | Keine | Gateway bei lokalen Quellen | Ein Hybridmodell | Fabric-Kapazität und OneLake |
| Einrichtungsaufwand | Gering | Mittel | Hoch | Gering, wenn Fabric bereits läuft |
| Am besten für | Die meisten Berichte | Echtzeit und sehr große Daten | Hybridmodelle | Fabric-native Modelle |

## Drei Punkte, die die Matrix zu Direct Lake verschweigt

Die Tabelle vergleicht, was die Modi versprechen. Bei Direct Lake gibt es drei Verhaltensweisen, die in der Praxis häufiger auftreten, als die Dokumentation vermuten lässt.

**Der Fallback ist stumm, bis Sie ihn messen.** Lässt sich eine DAX-Abfrage nicht aus den geladenen Spalten beantworten, greift das Modell je nach Einstellung auf DirectQuery zurück oder liefert einen Fehler. Ein stiller Fallback bedeutet: Der Bericht ist im Test schnell und in Produktion langsam, weil eine einzelne Measure einen Pfad auslöst, den die Vorschau-Metriken nie berührt haben. Prüfen Sie die Server-Timings und suchen Sie im Direct-Lake-Modell nach DirectQuery-Aktivität — wenn Sie welche finden, fällt etwas zurück.

**Framing ist keine Aktualisierung, kostet aber etwas.** Die erste Abfrage nach neuen Delta-Commits lädt die referenzierten Spalten erneut. Wird eine Tabelle häufig neu geschrieben, zahlt derjenige, der den Bericht zuerst öffnet. Die [Direct-Lake-Übersicht von Microsoft](https://learn.microsoft.com/de-de/fabric/fundamentals/direct-lake-overview) beschreibt die Regeln; in der Praxis zählt die erste Abfrage nach einem Pipeline-Lauf, nicht der Durchschnitt.

**Die Kapazität ist das eigentliche Hindernis.** Direct Lake setzt Fabric voraus. Wer heute mit einer Pro-Lizenz zwischen Import und DirectQuery entscheidet, für den ist dieser Modus noch keine Option — ihn in eine Vergleichstabelle aufzunehmen ist sinnvoll, ihn einzuplanen, bevor die Kapazität existiert, nicht.

## Ein Hybridmodell einrichten

In vielen Projekten braucht man beides: Tempo für die Historie und Aktualität für die letzten Buchungen. Genau dafür gibt es Hybridmodelle.

**Schritt 1 — Faktentabellen auf DirectQuery stellen:**
In Power BI Desktop in die **Modell**-Ansicht wechseln, die Faktentabelle auswählen, dann **Eigenschaften** → **Erweitert** → **Speichermodus** → **DirectQuery**.

**Schritt 2 — Dimensionstabellen auf Dual stellen:**
Jede Dimensionstabelle auswählen und den **Speichermodus** auf **Dual** setzen. Damit bleiben die Dimensionen im Speicher und die Verknüpfung zur Faktentabelle funktioniert ohne Umweg über die Quelle.

**Schritt 3 — Aggregationen anlegen (optional, aber empfohlen):**
Eine Aggregationstabelle fasst die Faktdaten auf den häufigsten Gruppierungsebenen vor. Passt eine Abfrage zum Aggregationsmuster, nutzt Power BI die Tabelle im Import-Modus und greift nur für Detailabfragen auf DirectQuery zurück.

```dax
-- Aggregationstabelle: Tagesumsatz je Kategorie
Tagesumsatz Agg =
SUMMARIZE(
    'Umsatz',
    'Datum'[Datum],
    'Produkt'[Kategorie],
    "Umsatz", SUM('Umsatz'[Betrag]),
    "Menge", SUM('Umsatz'[Menge])
)
```

Die Aggregationstabelle wird auf Import gestellt und anschließend über **Aggregationen verwalten** mit der DirectQuery-Faktentabelle verknüpft.

**Schritt 4 — Inkrementelle Aktualisierung einrichten:**
Für die Import-Tabellen im Hybridmodell lädt die inkrementelle Aktualisierung nur neue Daten statt alles neu. Wie das mit Parametern zusammenspielt, zeigt die Anleitung zu [berechneten Tabellen und What-if-Parametern](/tutorials/calculated-tables-what-if-parameters/).

## Auswirkungen auf die Performance

### Import

VertiPaq komprimiert je nach Datentyp etwa 3:1 bis 10:1. Eine Quelltabelle mit 1 GB landet meist bei 100 bis 300 MB im Speicher. Die Abfragegeschwindigkeit hängt ab von:

- der Spaltenanzahl — mehr Spalten kosten, weil VertiPaq spaltenorientiert arbeitet
- der Kardinalität — viele unterschiedliche Werte brauchen mehr Speicher
- dem Modelldesign — wenige breite Tabellen sind meist besser als viele schmale

### DirectQuery

Jedes Visual erzeugt SQL. Ein Bericht mit zehn Visuals auf einer Seite schickt zehn Abfragen gleichzeitig los. Die Leistung hängt vollständig ab von:

- der Geschwindigkeit der Quelldatenbank, also Indizes, Partitionen und Optimierer
- der Komplexität der Abfrage — DAX wird nach SQL übersetzt, komplexe DAX wird zu komplexem SQL
- der Zahl gleichzeitiger Nutzer
- der Netzwerklatenz zwischen Power BI und der Quelle

**Bewährte Regeln für DirectQuery:**

- Auf jeder Seite einen Datumsfilter setzen, der den abgefragten Zeitraum begrenzt
- Visuals mit hoher Kardinalität vermeiden, also keine Tabelle mit einer Million Zeilen
- Die Zahl der Visuals pro Seite klein halten, fünf bis sieben sind ein guter Richtwert
- Den Performance-Analyzer nutzen, um langsame Abfragen zu finden

### Hybridmodell

Der Erfolg eines Hybridmodells steht und fällt mit der Aggregationstabelle. Ohne sie dominieren die DirectQuery-Tabellen die Laufzeit, weil jede Abfrage bis zur Quelle durchfällt. Mit sauber gebauten Aggregationen treffen 80 bis 90 Prozent der Abfragen die speicherinterne Tabelle, und nur Detailansichten gehen an die Quelle.

## Fünf häufige Fehler

### 1. DirectQuery als Ersatz für Datenmodellierung

```
❌ DirectQuery direkt auf eine rohe Transaktionstabelle mit 50 Spalten und ohne Aggregation
✅ Aggregationstabelle im Import-Modus, DirectQuery nur für Detailabfragen
```

DirectQuery ersetzt kein sauberes Datenmodell. Ist der Bericht im DirectQuery-Modus langsam, liegt die Ursache meist im Modell oder in der Quellabfrage, nicht in Power BI.

### 2. Speichermodi falsch mischen

```
❌ Faktentabelle = Import, Dimensionstabelle = DirectQuery
   → Jede Verknüpfung erzwingt DirectQuery und kostet Tempo

✅ Faktentabelle = DirectQuery, Dimensionstabelle = Dual
   → Die Dimension liegt im Speicher, die Faktentabelle fragt nur bei Bedarf die Quelle
```

### 3. Vergessen, dass manche DAX-Funktionen nicht funktionieren

DirectQuery unterstützt nicht den gesamten DAX-Umfang. Häufig betroffen sind:

- Teile der Zeitintelligenz
- `PATH()` und die Funktionen für Eltern-Kind-Hierarchien
- einige statistische Funktionen
- berechnete Tabellen, die es gar nicht gibt

Power BI Desktop zeigt eine Warnung, sobald eine nicht unterstützte Funktion in einer DirectQuery-Measure auftaucht. Diese Warnung ist kein Hinweis, sondern ein Fehler, der im Betrieb auftritt.

### 4. Keine inkrementelle Aktualisierung für Import-Tabellen

```
❌ Jede Stunde fünf Jahre Daten vollständig neu laden → 20 Minuten Laufzeit
✅ Inkrementell nur die neuen Tage laden → 30 Sekunden Laufzeit
```

Die inkrementelle Aktualisierung wird über die Parameter `RangeStart` und `RangeEnd` gesteuert. Details zur Planung stehen in der Anleitung zur [Performance-Optimierung](/tutorials/power-bi-performance-optimization/).

### 5. DirectQuery ohne Gateway planen

Eine lokale SQL-Server-Instanz erreicht der Power BI-Dienst nur über ein Gateway. Wer den Speichermodus wählt, ohne die Netzwerkstrecke zu klären, bekommt einen Bericht, der im Desktop funktioniert und im Dienst nicht aktualisiert. Klären Sie deshalb vor der Modellierung, ob ein Gateway vorhanden ist und ob es die erwartete Last trägt.

## Häufige Fragen

**Kann ich den Speichermodus nachträglich ändern?**

Ja, aber es kann Beziehungen und Measures brechen. In der Modell-Ansicht die Tabelle auswählen, dann **Eigenschaften** → **Erweitert** → **Speichermodus**. Der Wechsel von Import zu DirectQuery entfernt alle berechneten Spalten und berechneten Tabellen dieser Tabelle.

**Wie viele gleichzeitige Nutzer hält DirectQuery aus?**

Das hängt allein von der Quelldatenbank ab. Ein gut eingestellter SQL Server verkraftet Hunderte gleichzeitiger Abfragen. Eine kleine PostgreSQL-Instanz kommt bei 20 an ihre Grenzen. Testen Sie mit realistischer Last, bevor Sie den Bericht freigeben.

**Funktioniert DirectQuery mit Excel- oder CSV-Dateien?**

Nein. DirectQuery braucht eine unterstützte Datenbankquelle wie SQL Server, Snowflake, Oracle oder PostgreSQL. Dateiquellen wie Excel, CSV und SharePoint-Listen unterstützen nur den Import-Modus.

**Geht Direct Lake ohne Fabric-Kapazität?**

Nein. Direct Lake ist eine Fabric-Funktion; eine reine Power BI Pro-Lizenz kann kein Direct-Lake-Modell hosten. Ohne Fabric bleiben Import und DirectQuery die beiden Optionen, Dual als Werkzeug für Hybridmodelle.

**Ersetzt Direct Lake den Import-Modus?**

Noch nicht, und nicht für alle. Es nimmt den Aktualisierungsplan und die zweite Datenkopie weg — die beiden Hauptgründe für Import. Aber die Daten müssen bereits als Delta in OneLake liegen, und manche DAX-Abfrage löst einen Fallback aus. Für ein Modell auf einem lokalen SQL Server ohne Fabric-Kapazität bleibt Import die richtige Antwort.

**Lässt sich Zeilenebene Sicherheit mit DirectQuery kombinieren?**

Ja. RLS funktioniert in beiden Modi. Bei DirectQuery werden die Filter als WHERE-Klausel an die Quelldatenbank weitergereicht. Wie das aufgebaut wird, steht in der Anleitung zur [Zeilenebenensicherheit](/tutorials/power-bi-row-level-security/).

**Wie oft sollte ein Import-Modell aktualisiert werden?**

Für die meisten Geschäftsberichte reichen acht Aktualisierungen pro Tag, also alle drei Stunden. Für operative Dashboards kann stündlich nötig sein. Power BI Pro erlaubt acht geplante Aktualisierungen pro Tag, Premium 48. Wer häufiger braucht, sollte DirectQuery oder Streaming-Datasets prüfen.

## Wie es weitergeht

Bevor Sie den Speichermodus festlegen, lohnt sich ein Blick auf das Modell selbst: [DAX Grundlagen](/tutorials/de-dax-basics/) erklärt Measures und Filterkontext, und [Bedingte Formatierung in Power BI](/tutorials/de-conditional-formatting-power-bi/) zeigt, wie Sie die Ergebnisse anschließend lesbar machen.

Die englische Originalfassung dieses Artikels finden Sie unter [Import vs DirectQuery vs Dual vs Direct Lake](/tutorials/directquery-vs-import-mode/).

## Weiterlesen

- [DAX Grundlagen](/tutorials/de-dax-basics/) — Measures, Filterkontext und die ersten Formeln.
- [Bedingte Formatierung in Power BI](/tutorials/de-conditional-formatting-power-bi/) — Werte per Regel, Feldwert oder Verlauf einfärben.
- [Import vs DirectQuery vs Dual vs Direct Lake](/tutorials/directquery-vs-import-mode/) — die englische Originalfassung.
- [Incremental Refresh in Power BI](/tutorials/power-bi-incremental-refresh/) — Aktualisierung nur für neue Daten.
- [Power BI Performance-Optimierung](/tutorials/de-power-bi-performance-optimization/) — langsame Berichte systematisch beschleunigen.
- [Power BI Service vs Desktop](/tutorials/power-bi-service-vs-desktop/) — was wo läuft.
