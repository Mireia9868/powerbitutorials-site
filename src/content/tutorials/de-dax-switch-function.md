---
title: "SWITCH in DAX: Syntax, vier Muster und warum das Ergebnis leer bleibt"
description: "SWITCH ersetzt verschachtelte WENN-Funktionen durch lesbare Logik. Vier Muster, die Reihenfolge der Auswertung und die Fehler, die zu einem leeren Ergebnis führen."
pubDate: 2026-11-21
updatedDate: 2026-11-21
category: "dax"
difficulty: "Intermediate"
tags: ["dax", "switch", "bedingte-logik", "dax-funktionen", "fehlerbehebung"]
author: Mireia
featured: false
draft: false
---

SWITCH ist die DAX-Funktion, die einen Ausdruck gegen mehrere mögliche Werte prüft und für jeden Treffer ein anderes Ergebnis zurückgibt. Sie ersetzt lange Ketten verschachtelter WENN-Funktionen durch eine flache, gut lesbare Struktur, die sich leichter pflegen und debuggen lässt.

Wer schon einmal `WENN(Bedingung1, Ergebnis1, WENN(Bedingung2, Ergebnis2, ...))` geschrieben und dabei die Klammern aus den Augen verloren hat, findet hier die Lösung. Diese Anleitung zeigt Syntax, vier Praxismuster, die Entscheidung zwischen SWITCH und WENN sowie die typischen Fehler, die zu leeren Ergebnissen führen. Die vollständige Syntax steht in der [Microsoft-Referenz zu SWITCH](https://learn.microsoft.com/de-de/dax/switch-function-dax); dieselbe Argumentliste mit Beispiel finden Sie in der [DAX-Funktionsreferenz](/tools/dax-functions/#switch).

## Die Syntax von SWITCH

```dax
SWITCH(
    <Ausdruck>,
    <Wert1>, <Ergebnis1>,
    <Wert2>, <Ergebnis2>,
    ...
    [<Sonst-Ergebnis>]
)
```

SWITCH wertet `<Ausdruck>` genau einmal aus und vergleicht das Ergebnis der Reihe nach mit jedem `<Wert>`. Beim ersten Treffer gibt die Funktion das zugehörige `<Ergebnis>` zurück. Passt kein Wert, wird das `<Sonst-Ergebnis>` zurückgegeben — fehlt auch dieses, liefert SWITCH einen leeren Wert (BLANK).

**Einfaches Beispiel — eine Punktzahl in eine Note übersetzen:**

```dax
Note = SWITCH(
    TRUE(),
    [Punkte] >= 90, "Sehr gut",
    [Punkte] >= 80, "Gut",
    [Punkte] >= 70, "Befriedigend",
    [Punkte] >= 60, "Ausreichend",
    "Nicht bestanden"
)
```

> **Das zentrale Muster:** Wenn Sie `TRUE()` als Ausdruck übergeben, behandelt SWITCH jeden Wert als boolesche Bedingung. Das ist die häufigste Verwendung, weil sich damit Bereichslogik (größer als, kleiner als) statt exakter Übereinstimmungen abbilden lässt.

## Muster 1: Kategorien zuordnen

Kurze Codes oder IDs werden zu lesbaren Bezeichnungen — der sauberste Anwendungsfall und ein direkter Ersatz für verschachtelte WENN-Funktionen.

```dax
Produktkategorie = SWITCH(
    Produkte[KategorieCode],
    "ELEC", "Elektronik",
    "HOME", "Haus & Garten",
    "APP", "Bekleidung",
    "FOOD", "Lebensmittel",
    "Sonstiges"
)
```

**Vorher (verschachteltes WENN — schwer zu lesen):**

```dax
Produktkategorie = 
WENN(Produkte[KategorieCode] = "ELEC", "Elektronik",
    WENN(Produkte[KategorieCode] = "HOME", "Haus & Garten",
        WENN(Produkte[KategorieCode] = "APP", "Bekleidung",
            WENN(Produkte[KategorieCode] = "FOOD", "Lebensmittel",
                "Sonstiges"
            )
        )
    )
)
```

Die SWITCH-Version ist kürzer, flacher und leichter um neue Kategorien zu erweitern: ein weiteres Werte-Ergebnis-Paar genügt.

## Muster 2: Wertebereiche in Klassen einteilen

Mit `TRUE()` als Ausdruck werden die Bedingungen der Reihe nach geprüft. SWITCH gibt den ersten Treffer zurück, deshalb ist die Reihenfolge entscheidend: Die engste Bedingung steht vorn.

```dax
Kundensegment = SWITCH(
    TRUE(),
    [Gesamtumsatz] >= 100000, "Bestandskunde",
    [Gesamtumsatz] >= 50000, "Mittelstand",
    [Gesamtumsatz] >= 10000, "Kleinbetrieb",
    [Gesamtumsatz] > 0, "Privatkunde",
    "Interessent"
)
```

Das entspricht einer Kette aus `WENN ... SONST WENN`, nur ohne Verschachtelung. Jede Bedingung wird von oben nach unten ausgewertet, und die erste, die TRUE liefert, gewinnt.

> **Reihenfolge beachten:** Würden Sie die Bedingungen umdrehen und `[Gesamtumsatz] > 0` nach vorn stellen, würde jeder Kunde mit irgendeinem Umsatz als "Privatkunde" eingestuft — kein Kunde käme je in die Stufen Mittelstand oder Bestandskunde.

## Muster 3: Measures dynamisch auswählen

Kombinieren Sie SWITCH mit einer Parametertabelle oder einem Datenschnitt, damit Anwender selbst wählen, welche Kennzahl das Visual zeigt — ein beliebtes Muster für flexible Berichtsseiten.

**Schritt 1 — Eine nicht verknüpfte Tabelle mit Measure-Namen anlegen:**

```dax
MeasureTabelle = 
DATATABLE(
    "MeasureName", STRING,
    "Sortierung", INTEGER,
    {
        {"Umsatz", 1},
        {"Rohertrag", 2},
        {"Menge", 3},
        {"Durchschnittlicher Bestellwert", 4}
    }
)
```

**Schritt 2 — In einem Measure per SWITCH die gewählte Berechnung zurückgeben:**

```dax
Gewähltes Measure = SWITCH(
    SELECTEDVALUE(MeasureTabelle[MeasureName]),
    "Umsatz", [Umsatz],
    "Rohertrag", [Rohertrag],
    "Menge", [Menge],
    "Durchschnittlicher Bestellwert", [Durchschnittlicher Bestellwert],
    BLANK()
)
```

Wählt der Anwender im Datenschnitt "Rohertrag", berechnet das Measure `[Rohertrag]`. Wechselt er auf "Menge", wird entsprechend diese Kennzahl berechnet. Ein Visual, vier verschiedene Werte.

## Muster 4: Ersatzwerte für BLANK

Mit SWITCH lassen sich Standardwerte setzen, wenn ein Measure leer zurückkommt — nützlich für Dashboards, in denen leere Zellen wie ein Fehler aussehen.

```dax
Umsatz mit Ersatzwert = SWITCH(
    TRUE(),
    ISBLANK([Umsatz]), 0,
    [Umsatz] < 0, 0,
    [Umsatz]
)
```

So zeigt das Visual immer eine Zahl statt einer Lücke, ohne die Logik für gültige Werte zu verändern.

## SWITCH oder WENN: Wann was?

| Kriterium | SWITCH | Verschachteltes WENN |
|-----------|--------|----------------------|
| Ab 3 Bedingungen | ✅ Sauber und flach | ❌ Tief verschachtelt, schwer lesbar |
| 1–2 Bedingungen | Funktioniert ebenfalls | ✅ Einfacher für einfache Fälle |
| Bereichslogik | ✅ Mit TRUE() | ✅ Von Haus aus |
| Exakte Zuordnung | ✅ Idealer Anwendungsfall | ⚠️ Geht, ist aber umständlich |
| Performance | ✅ Wertet den Ausdruck einmal aus | ⚠️ Prüft jede Bedingung erneut |
| Wartbarkeit | ✅ Einfach zu ergänzen und umzusortieren | ❌ Klammern im Blick behalten |

**Faustregel:** Sobald Sie mehr als zwei WENN-Funktionen verschachteln, wechseln Sie zu SWITCH.

## Häufige Fehler

### 1. Der Sonst-Zweig fehlt

```dax
-- ❌ Problem: Liefert BLANK, wenn keine Bedingung zutrifft
Status = SWITCH(
    TRUE(),
    [Tage überfällig] > 30, "Kritisch",
    [Tage überfällig] > 7, "Warnung"
)

-- ✅ Lösung: Sonst-Zweig ergänzen
Status = SWITCH(
    TRUE(),
    [Tage überfällig] > 30, "Kritisch",
    [Tage überfällig] > 7, "Warnung",
    "Im Plan"
)
```

### 2. Falsche Reihenfolge der Bedingungen

```dax
-- ❌ Problem: Die erste Bedingung fängt alles ab
Stufe = SWITCH(
    TRUE(),
    [Umsatz] > 0, "Bronze",
    [Umsatz] > 10000, "Silber",
    [Umsatz] > 50000, "Gold"
)
-- Jede Zeile mit Umsatz > 0 liefert "Bronze"

-- ✅ Lösung: Engste Bedingung zuerst
Stufe = SWITCH(
    TRUE(),
    [Umsatz] > 50000, "Gold",
    [Umsatz] > 10000, "Silber",
    [Umsatz] > 0, "Bronze",
    "Keine"
)
```

### 3. SWITCH ohne TRUE() für Bereichslogik

```dax
-- ❌ Problem: SWITCH vergleicht den Umsatz-WERT, nicht die Bedingung
Stufe = SWITCH(
    [Umsatz],
    [Umsatz] > 50000, "Gold",   -- vergleicht [Umsatz] mit WAHR/FALSCH
    "Sonstige"
)

-- ✅ Lösung: TRUE() als Ausdruck verwenden
Stufe = SWITCH(
    TRUE(),
    [Umsatz] > 50000, "Gold",
    "Sonstige"
)
```

### 4. Unterschiedliche Datentypen in den Rückgabewerten

```dax
-- ❌ Problem: Text und Zahl gemischt
Ergebnis = SWITCH(
    TRUE(),
    [Punkte] > 90, "Sehr gut",
    [Punkte] > 60, 1,           -- Zahl in einer Textspalte
    0
)

-- ✅ Lösung: Rückgabetypen einheitlich halten
Ergebnis = SWITCH(
    TRUE(),
    [Punkte] > 90, "Sehr gut",
    [Punkte] > 60, "Bestanden",
    "Nicht bestanden"
)
```

## Häufige Fragen

**F: Bricht SWITCH nach dem ersten Treffer ab (Short-Circuit)?**

Ja. SWITCH wertet den Ausdruck einmal aus und prüft dann die Werte der Reihe nach. Beim ersten Treffer wird das Ergebnis sofort zurückgegeben, die übrigen Paare bleiben ungeprüft — bei langen Ketten effizienter als verschachtelte WENN-Funktionen.

**F: Kann ich SWITCH innerhalb von SWITCH verschachteln?**

Ja, aber meist ein Zeichen dafür, dass die Logik anders strukturiert werden sollte — etwa über eine berechnete Spalte oder eine Zuordnungstabelle. Wenn es nicht anders geht, speichern Sie das innere Ergebnis zuerst mit `VAR` in einer Variablen; mehr dazu in der Anleitung zu [DAX-Variablen](/tutorials/dax-variables-guide/).

**F: Ist SWITCH in DAX schneller als verschachteltes WENN?**

In den meisten Fällen ja. SWITCH wertet den Ausdruck einmal aus und führt dann einfache Vergleiche durch, während verschachteltes WENN auf jeder Ebene erneut prüft. Bei zwei oder drei Bedingungen ist der Unterschied klein, mit längeren Ketten wächst er.

**F: Funktioniert SWITCH mit Platzhaltern oder CONTAINS-Logik?**

Nicht direkt, SWITCH vergleicht ausschließlich exakt. Für Mustererkennung kombinieren Sie `SEARCH()` oder `CONTAINSSTRING()` mit dem `TRUE()`-Muster:

```dax
Kategorie = SWITCH(
    TRUE(),
    CONTAINSSTRING([Produktname], "Laptop"), "Computer",
    CONTAINSSTRING([Produktname], "Telefon"), "Mobil",
    "Sonstiges"
)
```

**F: Wie viele Werte-Ergebnis-Paare verträgt SWITCH?**

Eine harte Obergrenze gibt es nicht, aber sehr lange SWITCH-Anweisungen (50 Paare und mehr) sind meist ein Hinweis darauf, dass eine Zuordnungstabelle mit `RELATED()` oder `LOOKUPVALUE()` die bessere Wahl ist — Muster zeigt unsere Anleitung zum [Sternschema](/tutorials/data-modeling-star-schema/).

## Wie es weitergeht

- Die Funktion, die hinter den meisten SWITCH-Measures steckt, gründlich lernen: [CALCULATE](/tutorials/calculate-function/)
- Verstehen, wann Bedingungen ausgewertet werden: [Filterkontext und Zeilenkontext](/tutorials/filter-context-row-context-explained/)
- SWITCH-Logik debuggen, wenn sie nicht das tut, was sie soll: [DAX-Fehlerbehebung](/tutorials/dax-troubleshooting-guide/)
- Sehen, wie SWITCH mit Ranglogik zusammenspielt: [DAX RANKX](/tutorials/dax-rankx-function/)

Zum Auffrischen der Grundlagen lesen Sie unsere deutsche Einsteigeranleitung [DAX Grundlagen](/tutorials/de-dax-basics/). Wie Sie die Ergebnisse Ihrer SWITCH-Measures im Bericht sofort lesbar machen, zeigt [Bedingte Formatierung in Power BI](/tutorials/de-conditional-formatting-power-bi/). Die englische Originalfassung dieses Artikels finden Sie unter [DAX SWITCH: Syntax, 4 Patterns, and Why It Returns Blank](/tutorials/dax-switch-function/).

- [DAX Grundlagen](/tutorials/de-dax-basics/) — Measures, Filterkontext und die ersten Formeln.
- [Bedingte Formatierung in Power BI](/tutorials/de-conditional-formatting-power-bi/) — Werte per Regel, Feldwert oder Verlauf einfärben.
- [DAX SWITCH (englische Originalfassung)](/tutorials/dax-switch-function/) — die englische Version dieses Artikels.
