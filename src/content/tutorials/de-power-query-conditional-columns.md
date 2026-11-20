---
title: "Bedingte Spalte in Power Query: Wenn-dann-Logik ohne M-Code"
description: "Eine bedingte Spalte in Power Query erzeugt neue Werte nach Wenn-dann-Regeln, ganz ohne M-Code. Der Dialog, verschachtelte Bedingungen, der erzeugte Code und die Muster zum Kategorisieren, Markieren und Gruppieren von Daten."
pubDate: 2026-11-20
updatedDate: 2026-11-20
category: "power-query"
difficulty: "Beginner"
tags: ["power-query", "bedingte-spalte", "wenn-dann", "m-language", "transformationen"]
author: Mireia
featured: false
draft: false
---

Bedingte Spalten erzeugen neue Spalten auf Basis von Wenn-dann-Logik — über eine grafische Oberfläche, ohne eine Zeile M-Code. Diese Anleitung zeigt den Dialog, verschachtelte Bedingungen, den darunterliegenden Code und die Muster, mit denen Sie Daten kategorisieren, markieren und in Klassen einteilen.

Wer aus Excel kommt, kennt die `WENN()`-Formel. Power Query hat dasselbe Konzept — Logik, die einen neuen Spaltenwert nach Regeln bestimmt —, aber mit einem visuellen Baustein statt verschachtelter Funktionsaufrufe. Hier sehen Sie, wann Sie den Dialog **Bedingte Spalte** nutzen, wann **Benutzerdefinierte Spalte** die bessere Wahl ist und welche Muster in der Praxis immer wieder auftauchen.

## Eine bedingte Spalte anlegen

### Schritt 1: Den Dialog öffnen

1. Wählen Sie im Power Query-Editor die Tabelle aus, die Sie bearbeiten wollen.
2. Wechseln Sie im Menüband auf die Registerkarte **Spalte hinzufügen**.
3. Klicken Sie auf **Bedingte Spalte**.

### Schritt 2: Die Bedingung konfigurieren

Der Dialog zeigt einen visuellen Regelbaukasten:

- **Neuer Spaltenname:** wie das Ergebnis heißen soll
- **Wenn:** Spalte, Operator und Vergleichswert auswählen
- **Dann:** der Ausgabewert, wenn die Bedingung zutrifft
- **Sonst:** der Ausgabewert, wenn sie nicht zutrifft
- **Klausel hinzufügen:** eine weitere Wenn-dann-Regel anhängen (wird der Reihe nach geprüft)

Ein Beispiel: Aufträge nach Bestellwert einteilen.

| Einstellung | Wert |
|---------|-------|
| Neuer Spaltenname | Auftragsgröße |
| Wenn | `[Bestellwert]` `ist größer als` `10000` |
| Dann | `"Groß"` |
| Sonst | `"Klein"` |

Auf **OK** klicken, und Power Query legt die Spalte an. Ohne Code.

### Schritt 3: Das Ergebnis prüfen

Die neue Spalte erscheint am Ende der Tabelle. Power Query prüft jede Zeile gegen die Bedingung und setzt den passenden Wert. Der Datentyp wird automatisch auf Text gesetzt (oder auf Zahl, je nach Ausgabewerten).

**Tipp:** Prüfen Sie den Datentyp nach dem Anlegen immer. Power Query vergibt gelegentlich `Any`, und dieser Typ verursacht später Folgefehler. Klicken Sie auf das Typensymbol neben dem Spaltennamen und setzen Sie ihn explizit.

## Mehrere Bedingungen kombinieren

Mit **Klausel hinzufügen** hängen Sie weitere Wenn-dann-Regeln an. Geprüft wird von oben nach unten — die erste zutreffende Regel gewinnt:

| Wenn | Dann |
|----|------|
| `[Bestellwert]` `ist größer als` `10000` | `"Groß"` |
| `[Bestellwert]` `ist größer als` `5000` | `"Mittel"` |
| Sonst | `"Klein"` |

Damit landet jeder Auftrag in genau einer der drei Klassen. Ein Auftrag über 7.500 € trifft die zweite Regel (Mittel), weil die erste (größer als 10.000) nicht zutrifft. Ein Auftrag über 3.000 € trifft keine Regel und fällt auf Sonst (Klein) zurück.

**Wichtig:** Die Reihenfolge entscheidet. Setzen Sie die spezifischste bzw. die höchste Schwelle nach oben. Drehen Sie die Reihenfolge um und prüfen zuerst `> 5000`, wird jeder Auftrag über 5.000 € als Mittel eingestuft — auch die über 10.000 €.

## Verfügbare Operatoren

Der Dialog bietet je nach Datentyp der Spalte unterschiedliche Operatoren:

**Textspalten:**
- ist gleich / ist ungleich
- beginnt mit / beginnt nicht mit
- endet mit / endet nicht mit
- enthält / enthält nicht

**Zahlenspalten:**
- ist gleich / ist ungleich
- ist größer als / ist größer als oder gleich
- ist kleiner als / ist kleiner als oder gleich
- ist zwischen

**Datumsspalten:**
- ist gleich / ist ungleich
- ist vor / ist am oder vor
- ist nach / ist am oder nach
- ist zwischen

**Hinweis:** Der Operator „ist zwischen" steht nur im Dialog für benutzerdefinierte Spalten zur Verfügung, nicht in der bedingten Spalte. Für Zwischenbereiche formulieren Sie zwei Bedingungen (größer oder gleich X und kleiner oder gleich Y) oder weichen auf die benutzerdefinierte Spalte aus.

## Der M-Code dahinter

Jede bedingte Spalte erzeugt im Hintergrund M-Code. Sie sehen ihn über **Ansicht → Erweiterter Editor** oder in der Formelleiste (`fx`):

```powerquery
// Einfache bedingte Spalte
= if [Bestellwert] > 10000 then "Groß" else "Klein"

// Mehrere Bedingungen
= if [Bestellwert] > 10000 then "Groß"
  else if [Bestellwert] > 5000 then "Mittel"
  else "Klein"
```

**Regeln der M-Syntax:**
- `if`, `then` und `else` sind Schlüsselwörter in Kleinbuchstaben (M unterscheidet Groß- und Kleinschreibung).
- Vergleiche nutzen die üblichen Operatoren: `>`, `<`, `=`, `>=`, `<=`, `<>`.
- Textwerte stehen in doppelten Anführungszeichen: `"Groß"`.
- `and` / `or` verknüpfen Bedingungen: `if [Betrag] > 100 and [Status] = "Bezahlt" then …`

Den M-Code zu verstehen hilft, sobald Sie Logik brauchen, die der visuelle Baukasten nicht abbildet.

## Bedingte Spalte oder benutzerdefinierte Spalte?

| Merkmal | Bedingte Spalte | Benutzerdefinierte Spalte |
|---------|-------------------|--------------|
| Einfaches Wenn-dann | ✓ Visueller Baukasten | ✓ M-Code schreiben |
| Mehrere Bedingungen | ✓ Klausel hinzufügen | ✓ else-if-Ketten |
| UND-/ODER-Logik | ✗ Nicht unterstützt | ✓ mit `and`, `or` |
| Andere Spalten im Ergebnis | ✗ Nur feste Werte | ✓ Beliebiger Ausdruck |
| Verschachtelte Funktionen | ✗ | ✓ Jede M-Funktion |
| Zwischenbereiche | ✗ Zwei Bedingungen | ✓ `>= and <=` |

**Faustregel:** Erst die bedingte Spalte versuchen. Wenn der Dialog nicht ausdrückt, was Sie brauchen (UND-/ODER-Logik, dynamische Ausgabewerte, Funktionsaufrufe), zur benutzerdefinierten Spalte wechseln und den M-Code schreiben.

## Muster 1: Zahlen in Klassen einteilen

Der häufigste Fall — kontinuierliche Werte in diskrete Kategorien überführen:

```powerquery
// Dialog "Bedingte Spalte":
// Wenn [Umsatz] > 50000 dann "Enterprise"
// Sonst wenn [Umsatz] > 10000 dann "Mittelstand"
// Sonst wenn [Umsatz] > 1000 dann "KMU"
// Sonst "Gründung"
```

Oder direkt als M-Code:

```powerquery
= if [Umsatz] > 50000 then "Enterprise"
  else if [Umsatz] > 10000 then "Mittelstand"
  else if [Umsatz] > 1000 then "KMU"
  else "Gründung"
```

## Muster 2: Zeilen anhand von Text markieren

Aufträge kennzeichnen, die Aufmerksamkeit brauchen:

```powerquery
// Wenn [Status] gleich "Storniert" dann "Prüfen"
// Sonst wenn [Status] gleich "Erstattet" dann "Prüfen"
// Sonst wenn [Status] gleich "Offen" und [TageOffen] > 7 dann "Überfällig"
// Sonst "OK"
```

**Hinweis:** Die dritte Bedingung nutzt UND-Logik, die der Dialog nicht unterstützt. Für dieses Muster die benutzerdefinierte Spalte verwenden:

```powerquery
= if [Status] = "Storniert" then "Prüfen"
  else if [Status] = "Erstattet" then "Prüfen"
  else if [Status] = "Offen" and [TageOffen] > 7 then "Überfällig"
  else "OK"
```

## Muster 3: Nach Datum kategorisieren

Datensätze nach Alter einteilen:

```powerquery
// M-Code der benutzerdefinierten Spalte:
= if [Bestelldatum] >= Date.From(Date.AddDays(DateTime.LocalNow(), -30)) then "Aktuell"
  else if [Bestelldatum] >= Date.From(Date.AddDays(DateTime.LocalNow(), -90)) then "Dieses Quartal"
  else if [Bestelldatum] >= Date.From(Date.AddDays(DateTime.LocalNow(), -365)) then "Dieses Jahr"
  else "Älter"
```

`DateTime.LocalNow()` liefert das heutige Datum dynamisch. Die Einteilung aktualisiert sich damit bei jeder Aktualisierung der Abfrage von selbst — ohne dass Sie Schwellenwerte von Hand nachziehen müssen.

## Muster 4: Ersatzwerte für NULL

Leere Werte durch einen Standardwert ersetzen:

```powerquery
// Wenn [Rabatt] gleich null dann 0
// Sonst [Rabatt]
```

Als M-Code:

```powerquery
= if [Rabatt] = null then 0 else [Rabatt]
```

**Alternative:** der NULL-Operator `??`, eine Kurzform für genau dieses Muster:

```powerquery
= [Rabatt] ?? 0
```

`??` gibt den linken Wert zurück, wenn er nicht NULL ist, sonst den rechten. Für den einfachen NULL-Ersatz ist das sauberer als eine Wenn-dann-Konstruktion.

## Häufige Fehler

### 1. Groß- und Kleinschreibung bei Textvergleichen

M unterscheidet Groß- und Kleinschreibung. `"Bezahlt"` und `"bezahlt"` sind zwei verschiedene Werte:

```powerquery
// Trifft nur exakt "Bezahlt" — "BEZAHLT" und "bezahlt" laufen ins Sonst
= if [Status] = "Bezahlt" then "Abgeschlossen" else "Offen"

// Vergleich ohne Rücksicht auf Groß-/Kleinschreibung
= if Text.Lower([Status]) = "bezahlt" then "Abgeschlossen" else "Offen"
```

**Lösung:** Vor dem Vergleich mit `Text.Lower()` oder `Text.Upper()` normalisieren — oder in `Text.Equals()` den Vergleich `Comparer.OrdinalIgnoreCase` verwenden.

### 2. Umgang mit NULL

In M verhalten sich NULL-Vergleiche anders als in vielen anderen Sprachen. In der bedingten Spalte wählen Sie den Operator **ist gleich** und tippen `null` ohne Anführungszeichen. Im M-Code funktioniert `= null` korrekt:

```powerquery
// Ersetzt leere Werte durch "Leer"
= if [Wert] = null then "Leer" else "Vorhanden"
```

Im Dialog für die bedingte Spalte ist genau das der Weg — nicht der Versuch, `"null"` als Text zu vergleichen. Wer `"null"` in Anführungszeichen eingibt, sucht nach dem Wort, nicht nach dem leeren Wert.

### 3. Das Sonst vergessen

Jede Bedingung braucht ein Sonst. Fehlt es im M-Code, meldet Power Query einen Syntaxfehler. Im Dialog ist das Sonst Pflichtfeld — es fängt alle Zeilen ab, die keine Bedingung erfüllen.

```powerquery
// FALSCH — ohne Sonst, Syntaxfehler
= if [Wert] > 100 then "Hoch"

// Richtig
= if [Wert] > 100 then "Hoch" else "Niedrig"
```

### 4. Falscher Datentyp für die Ausgabewerte

Wenn Sie in derselben Spalte Text und Zahlen mischen, entsteht eine Spalte vom Typ `Any`, die später Fehler verursacht:

```powerquery
// Gemischte Typen — erzeugt Any, verursacht Folgefehler
= if [Punkte] > 90 then "A" else 0

// Einheitliche Typen — erzeugt eine Textspalte
= if [Punkte] > 90 then "A" else "F"
```

**Lösung:** Ausgabewerte innerhalb einer bedingten Spalte typgleich halten. Brauchen Sie gemischte Typen, legen Sie getrennte Spalten an oder stellen alles als Text dar.

## Häufige Fragen

**Kann ich im Dann-Wert auf eine andere Spalte verweisen?**
Im Dialog der bedingten Spalte nicht — das Dann-Feld akzeptiert nur feste Werte. Für einen Spaltenverweis die benutzerdefinierte Spalte nutzen: `= if [Status] = "Aktiv" then [Umsatz] else 0`.

**Wie viele Bedingungen sind möglich?**
Es gibt keine harte Obergrenze, aber jede Bedingung wird der Reihe nach geprüft. Ab etwa fünf bis sechs Bedingungen ist eine Nachschlagetabelle mit `Table.Lookup` oder ein Merge meist wartbarer.

**Aktualisiert sich die bedingte Spalte, wenn sich die Quelldaten ändern?**
Ja. Die Bedingung ist Teil der Abfrageschritte und wird bei jeder Aktualisierung neu ausgewertet. Wollen Sie Schwellenwerte ändern, bearbeiten Sie den Schritt unter **Angewendete Schritte**.

**Funktionieren bedingte Spalten mit berechneten Tabellen in DAX?**
Nein. Bedingte Spalten entstehen in Power Query (M), bevor die Daten die DAX-Engine erreichen. Brauchen Sie die Logik erst nach dem Laden, verwenden Sie eine berechnete DAX-Spalte mit `IF()` oder `SWITCH()`.

**Wie lautet die Wenn-dann-Syntax in Power Query?**
In einer benutzerdefinierten Spalte: `if [Punkte] > 90 then "A" else "B"`. Die Schlüsselwörter stehen klein und unterscheiden Groß-/Kleinschreibung. Der Dialog der bedingten Spalte baut dieselbe Logik visuell — seine Felder Wenn / Dann / Sonst entsprechen `if` / `then` / `else`.

**Wie gehe ich mit NULL in einer bedingten Spalte um?**
Mit `if [Rabatt] = null then 0 else [Rabatt]` oder der Kurzform `[Rabatt] ?? 0`. Im Dialog wählen Sie den Operator **ist gleich** und tippen `null` ohne Anführungszeichen.

## Wie es weitergeht

Wenn die Daten erst einmal klassifiziert sind, geht es an die eigentliche Auswertung. Unsere deutsche Einsteigeranleitung [Power Query für Einsteiger](/tutorials/de-power-query-getting-started/) zeigt die übrigen Grundtransformationen, und [DAX Grundlagen](/tutorials/de-dax-basics/) erklärt, wie Sie die vorbereiteten Spalten im Modell auswerten.

Die englische Originalfassung dieses Artikels finden Sie unter [Power Query: Add a Column With an If Statement](/tutorials/power-query-conditional-columns/).

Zum Weiterlesen:

- [Power Query für Einsteiger](/tutorials/de-power-query-getting-started/) — der Editor, die wichtigsten Transformationen und Query Folding.
- [DAX Grundlagen](/tutorials/de-dax-basics/) — Measures, Filterkontext und die ersten Formeln.
- [Power Query: Add a Column With an If Statement](/tutorials/power-query-conditional-columns/) — die englische Originalfassung.

Die hier beschriebene Funktionsweise folgt der [Microsoft-Dokumentation zum Hinzufügen einer bedingten Spalte](https://learn.microsoft.com/de-de/power-query/add-conditional-column).
