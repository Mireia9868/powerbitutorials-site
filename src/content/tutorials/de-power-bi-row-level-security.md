---
title: "Zeilenebene Sicherheit (RLS) in Power BI einrichten: statisch und dynamisch"
description: "RLS in Power BI richtig aufsetzen: statische und dynamische Rollen, USERPRINCIPALNAME, Sicherheitstabellen und die Fehler, durch die Nutzer trotzdem alles sehen."
pubDate: 2026-11-26
updatedDate: 2026-11-26
category: "data-modeling"
difficulty: "Intermediate"
tags: ["rls", "zeilenebene-sicherheit", "dynamisches-rls", "power-bi", "datenmodellierung"]
author: Mireia
featured: false
draft: false
---

Zeilenebene Sicherheit (Row Level Security, RLS) filtert Daten in Power BI danach, wer den Bericht öffnet. Die Vertriebsleitung in Hamburg sieht den Norden, die Kollegin in München den Süden, der Vorstand alles — und das im selben Bericht auf demselben Datenmodell, ohne dass jemand eine zweite Datei pflegen muss.

Der Teufel steckt nicht in der DAX-Formel, sondern im Betrieb: in der Zuordnung der Benutzer, in der Frage, ob der Filter wirklich bis zur Faktentabelle durchläuft, und in Kennzahlen, die den Filter mit `ALL()` wieder aushebeln. Diese Anleitung zeigt beide Varianten von RLS, die Sicherheitstabelle, die sie wartbar macht, und die vier Fehler, die in der Praxis am häufigsten dazu führen, dass ein Nutzer zu viel sieht.

## So arbeitet RLS

RLS legt einen DAX-Filter auf eine Tabelle im Modell. Sobald ein Benutzer den Bericht öffnet, wendet die Power-BI-Engine diesen Filter an, bevor irgendein Visual zeichnet. Der Benutzer sieht die ausgefilterten Zeilen nicht — und kann den Filter nicht umgehen, weil er nicht im Bericht, sondern in der Abfrage sitzt.

Entscheidend ist die Filterausbreitung: Ein RLS-Filter verhält sich wie jeder andere Filter im Modell und läuft über die Beziehungen weiter. Setzen Sie die Regel auf die Dimensionstabelle `Region`, erreicht sie über die Eins-zu-viele-Beziehung automatisch jede verbundene Faktentabelle. Sie müssen also nur die Dimension absichern, nicht jede Faktentabelle einzeln.

## Statisches RLS

Beim statischen RLS bekommt jede Rolle eine fest verdrahtete Filterregel. Der Ausdruck enthält einen konkreten Wert und ändert sich nicht, je nachdem wer den Bericht öffnet.

### Schritt 1: Rollen in Power BI Desktop anlegen

1. Wechseln Sie auf die Registerkarte **Modellieren**.
2. Klicken Sie auf **Rollen verwalten**.
3. Legen Sie mit **Neu** eine Rolle an.
4. Vergeben Sie einen sprechenden Namen, etwa „Region Nord“.
5. Wählen Sie die Tabelle, die gefiltert werden soll.
6. Tragen Sie den DAX-Ausdruck in das Feld ein.

### Schritt 2: Filterausdruck schreiben

Für eine Regionstabelle mit dem Firmensitz in Hamburg:

```dax
// Im Dialog "Rollen verwalten", auf der Tabelle Region:
[Region] = "Nord"
```

Aktiv ist die Rolle „Region Nord“ nur, wenn dieser Filter `Region[Region] = "Nord"` wahr ist. Über die Beziehung erreicht der Filter die Umsatztabelle, und der Bericht zeigt für diese Rolle ausschließlich norddeutsche Zeilen.

### Schritt 3: In Power BI Desktop testen

1. **Modellieren → Als Rolle anzeigen** öffnen.
2. Die Rolle „Region Nord“ anhaken.
3. Der Bericht zeigt jetzt nur noch die Nord-Daten.
4. Haken entfernen, um wieder die vollständige Sicht zu sehen.

### Schritt 4: Benutzer im Power BI Service zuweisen

1. Bericht in den Power BI Service veröffentlichen.
2. Beim Dataset unter **Sicherheit** die Rollen öffnen.
3. Benutzer oder Gruppen der jeweiligen Rolle hinzufügen.

**Die Grenze des statischen RLS:** Jede Rolle ist eine eigene Regel mit einem festen Wert. Bei 50 Regionen entstehen 50 Rollen, und jede Umstrukturierung des Vertriebsgebiets bedeutet Handarbeit in der Rollenverwaltung. Für ein Modell mit vielen Mandanten ist das nicht tragfähig.

## Dynamisches RLS

Dynamisches RLS kommt mit einer einzigen Rolle aus. Der Filter liest die Identität des angemeldeten Benutzers und schlägt seine Berechtigung in einer Sicherheitstabelle nach. Eine Rolle, beliebig viele Benutzer.

### Schritt 1: Sicherheitstabelle anlegen

Ergänzen Sie im Modell eine Tabelle, die Benutzer und Berechtigungskontext verbindet:

| E-Mail | Region |
|-------|--------|
| a.brinkmann@nordwind-handel.de | Nord |
| t.oezdemir@nordwind-handel.de | Süd |
| c.weber@nordwind-handel.de | Alle |

Verbinden Sie diese Tabelle über eine Beziehung mit der Dimension `Region`, und zwar in Richtung Sicherheit → Region, mit einfacher Filterrichtung.

### Schritt 2: Eine einzige Rolle anlegen

1. **Rollen verwalten** öffnen.
2. Eine Rolle „Dynamisches RLS“ anlegen.
3. Auf der Sicherheitstabelle diesen Filter eintragen:

```dax
// Sicherheitstabelle auf den aktuellen Benutzer filtern
[E-Mail] = USERPRINCIPALNAME()
```

`USERPRINCIPALNAME()` liefert die E-Mail-Adresse aus Microsoft Entra ID, also etwa `a.brinkmann@nordwind-handel.de`. Öffnet Frau Brinkmann den Bericht, wird die Sicherheitstabelle auf ihre Zeile reduziert, diese Zeile filtert die Region auf „Nord“, und der Filter läuft über die Beziehung bis in die Umsatztabelle.

### Schritt 3: Alle Benutzer der einen Rolle zuweisen

Im Power BI Service kommen alle Benutzer in die Rolle „Dynamisches RLS“. Jeder sieht andere Daten, obwohl es nur eine Rolle gibt — weil der Ausdruck für jeden anders ausgewertet wird.

## Das „Alle“-Muster

Für Vorstand, Controlling und Administration, die alles sehen dürfen, gibt es zwei Wege. Der naheliegende ist ein Sonderfall im Filter:

```dax
// Auf der Tabelle Region, nicht auf der Sicherheitstabelle:
[Region] =
    IF(
        LOOKUPVALUE(Sicherheit[Region], Sicherheit[E-Mail], USERPRINCIPALNAME()) = "Alle",
        [Region],
        LOOKUPVALUE(Sicherheit[Region], Sicherheit[E-Mail], USERPRINCIPALNAME())
    )
```

Das funktioniert, ist aber schwer zu lesen und zu prüfen — und es bricht, sobald jemand „alle“ klein schreibt.

**Besser:** eine m:n-Sicherheitstabelle mit einer Zeile je Benutzer-Region-Kombination. Wer alles sehen darf, bekommt für jede Region eine Zeile:

| E-Mail | Region |
|-------|--------|
| a.brinkmann@nordwind-handel.de | Nord |
| t.oezdemir@nordwind-handel.de | Süd |
| c.weber@nordwind-handel.de | Nord |
| c.weber@nordwind-handel.de | Süd |
| c.weber@nordwind-handel.de | Ost |
| c.weber@nordwind-handel.de | West |

Der Filter `[E-Mail] = USERPRINCIPALNAME()` liefert dann von selbst alle Zeilen von Frau Weber, und die Beziehung transportiert sie weiter. Kein Sonderfall, kein `LOOKUPVALUE`, keine Ausnahme im DAX. Die vollständige Referenz zu `ALL` und verwandten Funktionen steht in der [Microsoft-Dokumentation zu ALL](https://learn.microsoft.com/de-de/dax/all-function-dax).

## USERNAME() oder USERPRINCIPALNAME()?

Beide Funktionen liefern den aktuellen Benutzer, aber nicht denselben Wert — und zwar abhängig davon, wo der Bericht geöffnet wird:

| Funktion | Power BI Desktop | Power BI Service |
|----------|-----------------|-----------------|
| `USERNAME()` | `DOMAIN\Benutzer` | `benutzer@firma.de` |
| `USERPRINCIPALNAME()` | `benutzer@firma.de` | `benutzer@firma.de` |

**Verwenden Sie für RLS immer `USERPRINCIPALNAME()`.** Nur diese Funktion liefert in Desktop und Service dieselbe E-Mail-Adresse, also genau den Wert, der auch in der Sicherheitstabelle und in Microsoft Entra ID steht.

`USERNAME()` gibt im Desktop das Windows-Format `DOMAIN\Benutzer` zurück. Das passt zu keiner E-Mail-Spalte. Der typische Effekt: Im Service funktioniert die Rolle, beim Testen im Desktop sieht der Entwickler alles oder nichts — und sucht den Fehler dann im falschen Teil des Modells.

## Sicherheit über mehrere Dimensionen

Wenn eine Berechtigung von mehr als einer Dimension abhängt — jemand darf zum Beispiel bestimmte Regionen **und** nur bestimmte Produktkategorien sehen —, braucht die Sicherheitstabelle eine zusammengesetzte Struktur:

| E-Mail | Region | Produktkategorie |
|-------|--------|-----------------|
| a.brinkmann@nordwind-handel.de | Nord | Elektronik |
| a.brinkmann@nordwind-handel.de | Nord | Zubehör |
| t.oezdemir@nordwind-handel.de | Süd | Elektronik |

Der Filter `[E-Mail] = USERPRINCIPALNAME()` liefert alle passenden Zeilen. Die Beziehungen zu `Region` und `Produktkategorie` transportieren die Filter unabhängig voneinander in die jeweiligen Faktentabellen.

**Achtung:** Die Sicherheitstabelle braucht Beziehungen zu beiden Dimensionen, und beide müssen eine einfache Filterrichtung haben. Bidirektionale Filter an dieser Stelle erzeugen mehrdeutige Filterpfade und damit Ergebnisse, die sich nicht mehr erklären lassen.

## RLS und das Datenmodell

Ein RLS-Filter respektiert die Beziehungsrichtung im Modell. Drei Regeln reichen für die Praxis:

1. **Einfache Filterrichtung:** RLS auf einer Dimensionstabelle fließt zur Faktentabelle. Das ist das Standardmuster und der Fall, den Sie anstreben sollten.
2. **Bidirektionale Beziehungen:** Der Filter kann in beide Richtungen laufen, was aber ungewollte Filterwirkungen erzeugt. In Sicherheitsszenarien gehören bidirektionale Beziehungen nicht ins Modell.
3. **Beziehungslose Tabellen:** RLS auf einer Tabelle ohne Beziehung bewirkt nichts — es gibt keinen Pfad, über den der Filter weiterläuft.

**Faustregel:** RLS auf Dimensionstabellen setzen, nicht auf Faktentabellen. Die Dimension hat weniger Zeilen, der Filter ist schneller, und er erreicht über die Beziehungen trotzdem alle Faktentabellen.

## RLS testen

### In Power BI Desktop

1. **Modellieren → Als Rolle anzeigen**.
2. Rolle auswählen.
3. Der Bericht rendert mit dem Filter dieser Rolle.
4. Beim dynamischen RLS im Dialog „Als Rolle anzeigen“ eine konkrete E-Mail-Adresse eintragen, um einen bestimmten Benutzer zu simulieren.

### Im Power BI Service

1. Dataset → **Sicherheit**.
2. Neben dem Benutzernamen auf **Als Rolle testen** klicken.
3. Der Bericht öffnet sich im Testmodus und zeigt, was dieser Benutzer sieht.
4. Prüfen, ob die Zahlen den Erwartungen entsprechen — und zwar nicht nur die Summe, sondern auch ein Detail auf Zeilenebene.

### Typische Testbefunde

- **Alles leer:** Die E-Mail in der Sicherheitstabelle stimmt nicht mit der im Service überein. Häufig sind es Tippfehler, unterschiedliche Domains (`firma.onmicrosoft.com` statt `firma.de`) oder Groß-/Kleinschreibung.
- **Benutzer sieht zu viel:** Er ist mehreren Rollen zugeordnet, und eine davon hat keinen Filter. Wichtig: Wer keiner Rolle zugeordnet ist, sieht standardmäßig **alle** Daten. Jeder Benutzer muss mindestens einer RLS-Rolle angehören.
- **Benutzer sieht zu wenig:** In der Sicherheitstabelle steht die falsche Region, oder die Beziehung zwischen Sicherheitstabelle und Dimension fehlt beziehungsweise zeigt in die falsche Richtung.

## Häufige Fehler

### 1. Benutzer nicht zuweisen

Nach dem Veröffentlichen hat eine Rolle keine Mitglieder. Ohne Zuweisung im Power BI Service ist RLS für niemanden aktiv — alle sehen alles, und der Bericht wirkt fehlerfrei.

**Gegenmittel:** Nach jeder Veröffentlichung Dataset → Sicherheit öffnen und prüfen, ob jeder vorgesehene Benutzer in der richtigen Rolle steht.

### 2. USERNAME() statt USERPRINCIPALNAME()

Wie oben beschrieben: `USERNAME()` liefert im Desktop ein anderes Format als im Service. RLS funktioniert dann im Test und fällt im Produktivbetrieb um — der teuerste Fehler der Liste, weil er erst beim Kunden auffällt.

### 3. RLS auf der Faktentabelle

```dax
// FALSCH — filtert die Faktentabelle direkt, langsam und fehleranfällig
Filter auf Umsatz: [RegionKey] = LOOKUPVALUE(...)

// RICHTIG — filtert die Dimension, der Filter läuft über die Beziehung
Filter auf Region: [Region] = LOOKUPVALUE(Sicherheit[Region], Sicherheit[E-Mail], USERPRINCIPALNAME())
```

Die Variante auf der Faktentabelle muss jede Zeile einzeln prüfen. Bei einigen Millionen Umsatzzeilen ist das im DirectQuery-Modus ein spürbarer Unterschied — und sie bricht, sobald eine neue Faktentabelle dazukommt, die denselben Schutz braucht.

### 4. Kennzahlen mit ALL() hebeln RLS aus

```dax
// Diese Kennzahl ignoriert RLS — zeigt den Gesamtumsatz über alle Regionen
Umsatz Gesamt = CALCULATE([Umsatz], ALL(Region))
```

`ALL()` entfernt alle Filter von `Region` — auch den RLS-Filter. Eine Kennzahl, die so auf einer abgesicherten Tabelle arbeitet, kann Daten an Benutzer durchreichen, die sie nicht sehen dürfen. Das ist kein theoretisches Risiko: Es genügt eine Kachel „Gesamtumsatz“ im Bericht, und der Nord-Region-Leiter kennt den Umsatz aller Regionen.

**Gegenmittel:** Wo es der Zweck zulässt, `ALLSELECTED()` statt `ALL()` verwenden. `ALLSELECTED` respektiert RLS, weil es auf dem Filterkontext arbeitet, nachdem RLS angewendet wurde. Wenn `ALL()` wirklich nötig ist, prüfen Sie die Kennzahl gegen einen Testbenutzer mit eingeschränkter Rolle — nicht gegen Ihr eigenes Konto.

## FAQ

**Funktioniert RLS mit DirectQuery?**
Ja. RLS wird als WHERE-Klausel in die SQL-Abfrage an die Quelldatenbank übersetzt. Die Auswirkung auf die Performance hängt von der Indizierung der Quelltabelle und der Komplexität des Filters ab.

**Sehen Benutzer den RLS-Filter?**
Nein. RLS ist für Berichtsleser unsichtbar. Wer nicht mit einem anderen Benutzer vergleicht, weiß nicht, welche Zeilen fehlen.

**Lässt sich RLS mit eingebetteten Berichten nutzen?**
Ja, aber die einbettende Anwendung muss beim Erzeugen des Embed-Tokens eine effektive Identität mitgeben (E-Mail und optional Rolle). Ohne effektive Identität greift kein RLS.

**Addiert sich RLS zu RLS in der Quelldatenbank?**
Ja, beide Filter wirken unabhängig voneinander. Das Ergebnis ist die Schnittmenge: Ein Benutzer sieht nur Zeilen, die beide Prüfungen passieren.

**Kann ich RLS für einzelne Benutzer umgehen?**
Ja. Mitglieder mit Admin- oder Member-Rechten im Workspace können Rollen im Modus „Als Rolle anzeigen“ abwählen. Für einen serviceweiten Bypass lässt sich im Mandanten eine Ausnahme für Administratoren konfigurieren. Dokumentieren Sie solche Ausnahmen — sonst ist später unklar, warum eine Person mehr sieht als ihre Rolle erlaubt.

Bevor Sie RLS auf ein bestehendes Modell legen, lohnt ein Blick auf die Beziehungen: Ohne sauberes Sternschema mit einfachen Filterrichtungen wird jede Sicherheitsregel zur Fehlersuche. Wie das Modell aufgebaut sein sollte, steht in der Anleitung zum [Sternschema](/tutorials/data-modeling-star-schema/); wie Filterkontext und `ALL()` zusammenspielen, erklärt [CALCULATE in Power BI](/tutorials/de-calculate-function/).

## Weiterlesen

- [DAX Grundlagen: Measures, Filterkontext und die ersten Formeln](/tutorials/de-dax-basics/) — die Grundlage, auf der jeder RLS-Filter aufsetzt.
- [CALCULATE in Power BI: Filterkontext verstehen](/tutorials/de-calculate-function/) — warum `ALL()` RLS aushebelt und `ALLSELECTED()` nicht.
- [Power BI Row Level Security (RLS): Setup & Guidelines](/tutorials/power-bi-row-level-security/) — die englische Originalfassung dieses Artikels.
- [Bidirektionale Beziehungen in Power BI](/tutorials/bidirectional-filtering-guide/) — warum sie Sicherheitsfilter unberechenbar machen.
- [Power BI Performance-Optimierung](/tutorials/power-bi-performance-optimization/) — wenn RLS-Filter den Bericht ausbremsen.
