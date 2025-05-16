# PLANNING - E-commerce di pesca sportiva

## Obiettivi principali

- Creare una piattaforma di e-commerce dedicata alla pesca sportiva.
- Backend potente e flessibile con Django + Django REST Framework.
- Frontend veloce e SEO-ottimizzato con Next.js e Tailwind CSS.
- Integrazione completa con strumenti moderni (OAuth, AWS S3, PostgreSQL, ecc.).
- UX fluida, mobile-first e ottimizzata per tutte le risoluzioni.

---

## Tecnologie

### Backend
- Python (gestito con Poetry)
- Django
- Django REST Framework
- Django Allauth (Google login)
- PostgreSQL + pgAdmin
- boto3 + Django Storages (S3)
- Django Filters

### Frontend
- Next.js
- Tailwind CSS
- Framer Motion (animazioni leggere SEO-safe)
- SSR + SEO best practices (tag semantici, metatag dinamici, sitemap, robots.txt) evita "use client"

---

## Architettura

- **Backend REST API**: Tutta la logica di gestione di utenti, prodotti, ordini, wishlist, ecc.
- **Frontend Next.js**: Interfaccia utente SSR, con fetch ai dati tramite API Django.
- **Storage immagini**: AWS S3 gestito via Django Storages e boto3.
- **Autenticazione**: Social login (Google) + gestione sessione/utente.

---

## Moduli principali

1. **Home Page**
2. **Shop**: Catalogo prodotti filtrabile
3. **Usato**: Area per articoli di seconda mano
4. **Blog**: Articoli SEO-friendly
5. **Contatti**: Form con validazione
6. **Profilo Utente**
7. **Wishlist** (solo autenticati)
8. **Carrello** personale
9. **Sistema di checkout**
10. **Admin backend Django**

---

## Best practice

- Mobile-first
- SSR (Server-side rendering)
- Componenti riutilizzabili e modulare
- Routing Next.js ottimizzato
- Breadcrumbs + Sitemap + Metatag dinamici
- Performance optimization (lazy load, code splitting, compressione immagini)
- Evita "use client"
