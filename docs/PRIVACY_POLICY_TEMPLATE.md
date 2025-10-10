# Datenschutzerklärung / Privacy Policy

**Hinweis:** Dieses Template deckt grundlegende DSGVO-Anforderungen ab. Bei produktivem Betrieb unbedingt rechtliche Beratung einholen!

**Letzte Aktualisierung:** [DATUM]

---

## 1. Verantwortlicher

Verantwortlich für die Datenverarbeitung auf dieser Plattform:

**[DEIN NAME / FIRMENNAME]**
[ADRESSE]
[E-MAIL]
[OPTIONAL: TELEFON]

---

## 2. Welche Daten wir sammeln

### 2.1 Account-Daten
Bei der Registrierung speichern wir:
- Benutzername
- E-Mail-Adresse
- Passwort (verschlüsselt/gehasht)
- Registrierungsdatum

### 2.2 Nutzungsdaten
Bei der Nutzung der Plattform speichern wir:
- Generierte Inhalte (Bilder, Songs, Prompts)
- Metadaten (Titel, Tags, Bewertungen, Workflow-Status)
- Zeitstempel (Erstellungs- und Änderungsdatum)
- API-Job-IDs (für Tracking von Generierungsprozessen)

### 2.3 Technische Daten
- IP-Adresse (für Session-Management und Sicherheit)
- Browser-Typ und Version
- Zugriffszeitpunkte

### 2.4 API-Keys (Bring Your Own Key)
**WICHTIG:** Sie geben Ihre eigenen API-Keys (OpenAI, Mureka, etc.) in die Plattform ein.
- Diese werden verschlüsselt in unserer Datenbank gespeichert
- Wir verwenden diese AUSSCHLIESSLICH um Ihre Anfragen an die entsprechenden Dienste weiterzuleiten
- **Wir geben Ihre API-Keys NIEMALS an Dritte weiter**
- Sie können Ihre API-Keys jederzeit löschen oder ändern

---

## 3. Wie wir Ihre Daten verwenden

### 3.1 Zweck der Datenverarbeitung
Ihre Daten werden verwendet für:
- Bereitstellung der Plattform-Funktionalität
- Speicherung Ihrer generierten Inhalte (Bilder, Songs)
- Weiterleitung von Anfragen an Drittanbieter-APIs (mit Ihren eigenen API-Keys)
- Technische Sicherheit und Betrieb der Plattform
- Einhaltung gesetzlicher Verpflichtungen

### 3.2 Rechtsgrundlage (DSGVO)
- Art. 6 Abs. 1 lit. b DSGVO (Vertragserfüllung)
- Art. 6 Abs. 1 lit. f DSGVO (berechtigtes Interesse an sicherem Betrieb)
- Art. 6 Abs. 1 lit. a DSGVO (Einwilligung bei optionalen Features)

---

## 4. Datenspeicherung

### 4.1 Speicherort
Ihre Daten werden gespeichert in:
- PostgreSQL-Datenbank (gehostet in [LAND/REGION - z.B. Schweiz/Deutschland])
- Redis-Cache (temporär, Session-Daten)
- Lokaler Dateispeicher (generierte Medien: Bilder, Audio-Dateien)

### 4.2 Speicherdauer
- Account-Daten: Bis zur Löschung Ihres Accounts
- Generierte Inhalte: Bis zur manuellen Löschung durch Sie
- Technische Logs: [ANZAHL TAGE - z.B. 30 Tage]
- API-Keys: Bis zur Löschung durch Sie oder Ihres Accounts

---

## 5. Drittanbieter-Services (Third-Party APIs)

### 5.1 Bring Your Own Key (BYOK)
Sie verwenden Ihre eigenen API-Keys für:
- **OpenAI / DALL-E 3** (Bildgenerierung)
- **Mureka** (Musikgenerierung)
- **Weitere Dienste** (je nach Konfiguration)

### 5.2 Datenübertragung
Wenn Sie Inhalte generieren, werden **Ihre Prompts und Anfragen** an diese Drittanbieter übertragen:
- OpenAI: [Link zur OpenAI Privacy Policy - https://openai.com/privacy]
- Mureka: [Link zur Mureka Privacy Policy]

**WICHTIG:**
- Wir übertragen NUR die für die Generierung notwendigen Daten (Prompt, Parameter)
- Die Drittanbieter verarbeiten Ihre Anfragen gemäß deren eigenen Datenschutzrichtlinien
- Sie sind selbst verantwortlich für die Einhaltung der Terms of Service der Drittanbieter
- Wir haben KEINEN Einfluss auf die Datenverarbeitung durch Drittanbieter

### 5.3 Keine Haftung für Drittanbieter
Wir übernehmen keine Verantwortung für:
- Datenschutzpraktiken der Drittanbieter
- Kosten oder Gebühren der Drittanbieter
- Verfügbarkeit oder Qualität der Drittanbieter-Services

---

## 6. Cookies und Tracking

### 6.1 Notwendige Cookies
Wir verwenden Session-Cookies für:
- Authentifizierung (Login-Status)
- Sicherheit (CSRF-Protection)
- Session-Management

### 6.2 Optionale Cookies
[FALLS ZUTREFFEND:]
- Analytics (z.B. Google Analytics) - NUR mit Ihrer Einwilligung
- Präferenzen (UI-Einstellungen)

### 6.3 Cookie-Verwaltung
Sie können Cookies jederzeit in Ihren Browser-Einstellungen löschen oder blockieren. Dies kann jedoch die Funktionalität der Plattform beeinträchtigen.

---

## 7. Ihre Rechte (DSGVO)

Sie haben folgende Rechte bezüglich Ihrer Daten:

### 7.1 Auskunftsrecht (Art. 15 DSGVO)
Sie können jederzeit Auskunft über Ihre gespeicherten Daten verlangen.

### 7.2 Berichtigungsrecht (Art. 16 DSGVO)
Sie können fehlerhafte Daten korrigieren lassen.

### 7.3 Löschungsrecht (Art. 17 DSGVO)
Sie können die Löschung Ihrer Daten verlangen ("Recht auf Vergessenwerden").

### 7.4 Einschränkung der Verarbeitung (Art. 18 DSGVO)
Sie können die Einschränkung der Verarbeitung verlangen.

### 7.5 Datenübertragbarkeit (Art. 20 DSGVO)
Sie können Ihre Daten in einem strukturierten Format erhalten.

### 7.6 Widerspruchsrecht (Art. 21 DSGVO)
Sie können der Verarbeitung Ihrer Daten widersprechen.

### 7.7 Ausübung Ihrer Rechte
Um Ihre Rechte auszuüben, kontaktieren Sie uns unter:
**E-Mail:** [DEINE DATENSCHUTZ-E-MAIL]

Wir werden Ihre Anfrage innerhalb von 30 Tagen bearbeiten.

---

## 8. Datensicherheit

Wir treffen angemessene technische und organisatorische Maßnahmen zum Schutz Ihrer Daten:
- Verschlüsselte Datenbankverbindungen (PostgreSQL SSL/TLS)
- Passwort-Hashing (bcrypt/Argon2)
- Verschlüsselte Speicherung von API-Keys
- HTTPS-Verschlüsselung für alle Verbindungen
- Regelmäßige Sicherheits-Updates
- Zugriffsbeschränkungen (nur autorisiertes Personal)

**WICHTIG:** Keine Datenübertragung über das Internet ist zu 100% sicher. Wir können absolute Sicherheit nicht garantieren.

---

## 9. Account-Löschung

Sie können Ihren Account jederzeit löschen:
1. In den Account-Einstellungen "Account löschen" wählen
2. ODER E-Mail an [SUPPORT-E-MAIL]

Bei Löschung werden folgende Daten entfernt:
- Account-Daten (Name, E-Mail, Passwort)
- Alle gespeicherten API-Keys
- Alle generierten Inhalte (Bilder, Songs)
- Alle Metadaten und Einstellungen

**Hinweis:** Backups können bis zu [ANZAHL TAGE - z.B. 30 Tage] aufbewahrt werden.

---

## 10. Änderungen dieser Datenschutzerklärung

Wir behalten uns vor, diese Datenschutzerklärung anzupassen, um sie an geänderte Rechtslagen oder bei Änderungen der Plattform anzupassen.

Bei wesentlichen Änderungen werden Sie per E-Mail oder durch einen Hinweis auf der Plattform informiert.

**Aktuelle Version:** [VERSION - z.B. 1.0]
**Letzte Änderung:** [DATUM]

---

## 11. Beschwerderecht

Sie haben das Recht, sich bei einer Datenschutz-Aufsichtsbehörde zu beschweren:

**Deutschland:**
Bundesbeauftragter für den Datenschutz und die Informationsfreiheit (BfDI)
https://www.bfdi.bund.de

**Schweiz:**
Eidgenössischer Datenschutz- und Öffentlichkeitsbeauftragter (EDÖB)
https://www.edoeb.admin.ch

**Österreich:**
Österreichische Datenschutzbehörde
https://www.dsb.gv.at

---

## 12. Kontakt

Bei Fragen zum Datenschutz kontaktieren Sie uns:

**E-Mail:** [DATENSCHUTZ-E-MAIL]
**Adresse:** [DEINE ADRESSE]

---

**Disclaimer:** Diese Datenschutzerklärung ist keine Rechtsberatung. Bei produktivem Betrieb konsultieren Sie einen Fachanwalt für IT-Recht oder Datenschutzbeauftragten.
