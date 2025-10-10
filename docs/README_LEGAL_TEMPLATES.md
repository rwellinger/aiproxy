# Legal Templates - README

Diese Templates enthalten die wichtigsten rechtlichen Dokumente für einen produktiven Betrieb der Plattform.

## ⚠️ WICHTIG

**Diese Templates sind KEINE Rechtsberatung!**

- Sie decken grundlegende Aspekte ab
- Bei produktivem Betrieb UNBEDINGT einen Fachanwalt für IT-Recht konsultieren
- Gesetze variieren je nach Land/Region
- DSGVO-Anforderungen können sich ändern

---

## 📋 Verfügbare Templates

### 1. IMPRESSUM_TEMPLATE.md
**Wann benötigt:** Sofort bei öffentlichem Betrieb (DE/CH/AT Pflicht)

**Was ausfüllen:**
- `[DEIN NAME / FIRMENNAME]`
- `[STRAßE UND HAUSNUMMER]`
- `[PLZ ORT]`
- `[LAND]`
- `[DEINE E-MAIL]`
- `[TELEFONNUMMER]` (optional)
- `[USt-IdNr]` (falls vorhanden)
- `[DATUM]` - aktuelles Datum

**Wo einbinden:** Footer der Webseite, Link "Impressum"

---

### 2. PRIVACY_POLICY_TEMPLATE.md
**Wann benötigt:** Bei Erhebung personenbezogener Daten (DSGVO-Pflicht)

**Was ausfüllen:**
- Alle `[PLATZHALTER]` mit deinen Daten
- `[LAND/REGION]` - Speicherort der Datenbank
- `[ANZAHL TAGE]` - Log-Aufbewahrungsdauer (empfohlen: 30 Tage)
- `[DATENSCHUTZ-E-MAIL]` - dedizierte E-Mail für Datenschutzanfragen
- `[VERSION]` - z.B. 1.0
- `[DATUM]` - aktuelles Datum

**Wichtige Punkte prüfen:**
- Cookie-Nutzung (Section 6) - anpassen falls du Analytics nutzt
- Speicherdauer (Section 4.2)
- Third-Party Services (Section 5) - Links zu OpenAI/Mureka Privacy Policies

**Wo einbinden:** Footer der Webseite, Link "Datenschutz" / "Privacy Policy"

---

### 3. TERMS_OF_SERVICE_TEMPLATE.md
**Wann benötigt:** Bei Account-Registrierung / Plattform-Nutzung

**Was ausfüllen:**
- `[PLATTFORM-NAME]` - Name deiner Plattform
- `[DEIN NAME / FIRMENNAME]`
- `[ADRESSE]`
- `[E-MAIL]`
- `[VERSION]` - z.B. 1.0
- `[DATUM]` - aktuelles Datum

**Wichtige Entscheidungen:**

#### Section 5.1 - Plattform-Kosten
Wähle eine Option:
- **Option A:** Kostenlos
- **Option B:** Freemium (Basis gratis, Premium kostenpflichtig)
- **Option C:** Vollständig kostenpflichtig

#### Section 13.1 - Rechtswahl
Wähle anwendbares Recht:
- Deutschland
- Schweiz
- Österreich

#### Section 13.2 - Gerichtsstand
Wähle Gerichtsstand: `[ORT]` - z.B. Zürich, München, Wien

**Wo einbinden:**
- Bei Registrierung: Checkbox "Ich akzeptiere die AGB"
- Footer der Webseite: Link "Terms of Service" / "AGB"

---

## 🔧 Verwendung der Templates

### Schritt 1: Templates kopieren
```bash
cp docs/IMPRESSUM_TEMPLATE.md docs/IMPRESSUM.md
cp docs/PRIVACY_POLICY_TEMPLATE.md docs/PRIVACY_POLICY.md
cp docs/TERMS_OF_SERVICE_TEMPLATE.md docs/TERMS_OF_SERVICE.md
```

### Schritt 2: Platzhalter ausfüllen
Alle `[PLATZHALTER]` durch deine Daten ersetzen:
- Name/Firma
- Adresse
- E-Mail
- Datum
- Entscheidungen treffen (Kosten-Modell, Rechtswahl, etc.)

### Schritt 3: Rechtliche Prüfung
**UNBEDINGT vor produktivem Betrieb:**
- Fachanwalt für IT-Recht konsultieren
- DSGVO-Konformität prüfen lassen
- Haftungsausschlüsse für deine spezifische Situation anpassen

### Schritt 4: In Plattform einbinden

#### Angular Frontend (aiwebui)
```typescript
// Neue Routes hinzufügen
{ path: 'impressum', component: ImpressumComponent },
{ path: 'privacy', component: PrivacyComponent },
{ path: 'terms', component: TermsComponent }

// Footer Component
<a routerLink="/impressum">Impressum</a>
<a routerLink="/privacy">Datenschutz</a>
<a routerLink="/terms">AGB</a>
```

#### Bei Registration
```html
<mat-checkbox formControlName="acceptTerms" required>
  Ich akzeptiere die
  <a routerLink="/terms" target="_blank">AGB</a> und
  <a routerLink="/privacy" target="_blank">Datenschutzerklärung</a>
</mat-checkbox>
```

---

## 📅 Checkliste vor Produktiv-Schaltung

### Rechtliches
- [ ] Impressum ausgefüllt und veröffentlicht
- [ ] Datenschutzerklärung ausgefüllt und veröffentlicht
- [ ] Terms of Service ausgefüllt und veröffentlicht
- [ ] Fachanwalt konsultiert
- [ ] DSGVO-Konformität geprüft
- [ ] Cookie-Banner implementiert (falls nötig)

### Third-Party APIs
- [ ] OpenAI Terms of Service gelesen und akzeptiert
- [ ] Mureka Terms of Service gelesen und akzeptiert
- [ ] API-Preise verstanden und dokumentiert
- [ ] Rate Limits der APIs bekannt

### Technisches
- [ ] HTTPS aktiviert (SSL/TLS-Zertifikat)
- [ ] Datenbankbackups eingerichtet
- [ ] API-Keys verschlüsselt gespeichert
- [ ] Logging und Monitoring aktiv
- [ ] Fehlerbehandlung implementiert

### Kommunikation
- [ ] Support-E-Mail eingerichtet (`[SUPPORT-E-MAIL]`)
- [ ] Datenschutz-E-Mail eingerichtet (`[DATENSCHUTZ-E-MAIL]`)
- [ ] Kontaktformular / Support-System vorhanden

---

## 🔄 Aktualisierung der Dokumente

### Wann aktualisieren?
- Bei Änderung der Plattform-Features
- Bei Änderung der Kostenstruktur
- Bei neuen Third-Party Services
- Bei Änderung der Datenschutzpraktiken
- Bei Änderung der Gesetzeslage

### Wie aktualisieren?
1. Dokument anpassen
2. Version hochzählen (z.B. 1.0 → 1.1)
3. Datum aktualisieren
4. Nutzer informieren (E-Mail + Plattform-Hinweis)
5. [ANZAHL TAGE - z.B. 30 Tage] Vorlaufzeit einhalten

---

## 📞 Support-E-Mail Struktur

Empfohlene E-Mail-Adressen:

```
support@[DEINE-DOMAIN]       # Allgemeine Support-Anfragen
privacy@[DEINE-DOMAIN]       # Datenschutz-Anfragen (DSGVO)
legal@[DEINE-DOMAIN]         # Rechtliche Anfragen
abuse@[DEINE-DOMAIN]         # Missbrauch melden
```

---

## 🌍 Mehrsprachigkeit

Aktuell: **Englisch** (rechtlich bindend)

Falls mehrsprachig (z.B. Deutsch):
- Englische Version ist rechtlich bindend
- Deutsche Übersetzung mit Disclaimer:
  ```
  Diese Übersetzung dient nur zur Information.
  Rechtlich bindend ist ausschließlich die englische Version.
  ```

---

## 🔗 Wichtige Links

### DSGVO / Datenschutz
- **DSGVO (EU):** https://dsgvo-gesetz.de/
- **BfDI (DE):** https://www.bfdi.bund.de
- **EDÖB (CH):** https://www.edoeb.admin.ch
- **DSB (AT):** https://www.dsb.gv.at

### Third-Party Policies
- **OpenAI Terms:** https://openai.com/policies/terms-of-use
- **OpenAI Privacy:** https://openai.com/privacy
- **OpenAI Usage:** https://openai.com/policies/usage-policies

### Rechtliche Beratung
- Fachanwalt für IT-Recht finden
- DSGVO-Datenschutzbeauftragten konsultieren (ab 20 Mitarbeitern Pflicht in DE)

---

## ⚖️ Disclaimer

**Diese Templates sind:**
- Eine Hilfestellung für grundlegende rechtliche Dokumente
- Basierend auf Best Practices und üblichen Formulierungen
- KEINE professionelle Rechtsberatung
- KEINE Garantie für rechtliche Korrektheit

**Bei produktivem Betrieb:**
- Konsultieren Sie einen Fachanwalt für IT-Recht
- Lassen Sie die Dokumente auf Ihre spezifische Situation anpassen
- Prüfen Sie regelmäßig auf Aktualität (Gesetzesänderungen)

---

**Erstellt:** [DATUM]
**Für Projekt:** mac_ki_service
**Basis:** DSGVO, deutsches/schweizer Recht
**Status:** Template - nicht produktionsreif ohne Anpassung
