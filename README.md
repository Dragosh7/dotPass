# dotPass – Offline Password Manager 

**dotPass** este o aplicație desktop pentru gestionarea securizată a parolelor, funcționând complet offline. Include criptare AES (Fernet), protecție cu master password și mod de urgență (`dummy vault`). Aplicația este disponibilă pentru Windows 10 și 11 sub formă de executabil standalone.

## 🔐 Funcționalități principale

- Criptare simetrică a bazei de date locale
- Generator de parole
- Verificare breșe de securitate (HaveIBeenPwned)
- Mod de urgență cu date fictive
- Alerte SMS

## 📦 Descărcare

> Nu este nevoie de instalare suplimentară. Nu este necesar Python, Git sau alte pachete.

| Sistem          | Link Descărcare              |
|-----------------|------------------------------|
| Windows 10      | [dotPass_win10.zip](https://github.com/Dragosh7/dotPass/releases/tag/v1.0) |
| Windows 11      | [dotPass_win11.zip](https://github.com/Dragosh7/dotPass/releases/tag/v1.0/dotPass_win11.zip) |

## 🧰 Utilizare

1. Descarcă și dezarhivează fișierul ZIP.
2. Deschide fișierul `dotPass.exe`.
3. La prima pornire, creează-ți un profil (nume + master password).
4. Adaugă conturi, vizualizează parole și folosește aplicația.

## 📝 Notă

Aceasta este o aplicație de tip proiect academic. Nu trimite date în cloud. Vault-ul este stocat local în `%APPDATA%\dotPass`.

---
