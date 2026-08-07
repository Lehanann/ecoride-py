# Contexte Projet EcoRide
### Profil
- Développeur solo.
- Projet personnel EcoRide.
- Stack Backend : FastAPI + SQLAlchemy Async + PostgreSQL.
- Stack Frontend : Next.js (App Router) + TypeScript.
- Objectif : plateforme de covoiturage avec différents rôles.

## 1. Architecture Backend
### Structure

```text


app/
├── routes/
├── services/
├── repositories/
├── schemas/
├── models/
├── core/
│ ├── settings.py
│ ├── security/
│ └── exceptions/
└── utils/
```

Architecture :
```text
Route
  ↓
Service
  ↓
Repository
  ↓
Database
```

Les services gèrent les règles métiers et lèvent les exceptions.

Les routes sont volontairement très légères.

---

## 2. Authentification
### JWT

JWT implémenté avec :
```text
PyJWT
```
Payload :
```json
{
  "sub": "8",
  "exp": 1785660678
}
```
Choix volontaire :
```python
sub = user.id #uniquement
```

Les rôles ne sont pas stockés dans le JWT.

Ils sont récupérés en base.

### Schemas
#### LoginSchema
```python
class LoginSchema(BaseModel):
    email: EmailStr
    password: str
```

#### TokenResponse
```python
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

#### TokenPayload
```python
class TokenPayload(BaseModel):
    sub: str
    exp: int | None = None
```

---

## 3. Password Security

Fichier :
```text
core/security/password_security.py
```
Utilise :
```text
passlib
bcrypt
```
Fonctions :
```python
create_password_hash()
verify_password()
```

## 4. Settings

Les variables d'environnement sont centralisées dans :
```text
settings.py
```
Exemple :
```text
JWT_SECRET_KEY
JWT_ALGORITHM
JWT_ACCESS_TOKEN_EXPIRE_MINUTES
```
Aucune lecture directe du .env dans le code métier.

## 5. Auth Utils

Fichier :
```text
app/utils/auth_utils.py
```
Fonctions :
```python
create_access_token()
decode_access_token()
```
Utilise :
```python
settings.JWT_SECRET_KEY
settings.JWT_ALGORITHM
```

## 6. AuthenticationService

Fichier :
```text
services/authentication_service.py
```
Fonction principale :
```python
authenticate_user(email, password)
```

Logique :
```text
Recherche utilisateur
  ↓
verify_password()
  ↓
retour utilisateur
```
Les erreurs utilisent les exceptions centralisées.

Par exemple :
```python
raise unauthorized(detail="Invalid credentials")
```

---

## 7. Passage LocalStorage → Cookie HttpOnly
#### Ancien système
```text
Authorization: Bearer JWT
localStorage
```
Supprimé.

#### Nouveau système
Cookie :
```python
response.set_cookie(
    key="access_token",
    value=token,
    httponly=True,
    secure=False,
    samesite="lax"
)
```
Le navigateur stocke automatiquement le JWT.

#### Middleware

Le middleware lit maintenant :

```python
request.cookies.get("access_token")
```
Puis :

```python
payload = decode_access_token(token)
request.state.user_id = int(payload.sub)
```
---

## 8. CORS

Important :

```python
allow_credentials=True
```

Frontend et backend utilisent désormais :
```text
http://localhost:3000
http://localhost:8000
```

Le mélange :
```text
localhost
127.0.0.1
```
cassait les cookies.
Problème résolu.

---

## 9. Routes Fonctionnelles
#### Login
```http
POST /auth/login
```
Fonctionnel.

#### Logout

En cours.

Prévu :

```python
response.delete_cookie(key="access_token")
```

#### Current User
```html
GET /users/me
```
Fonctionnel.
Retourne :
```json
{
  "id": ...,
  "roles": [...]
}
```

---

## 10. Frontend
### Services
#### api.ts
Wrapper central :
```typescript
apiFetch<T>()
```
Utilise :
```typescript
credentials: "include"
```
pour envoyer les cookies.

#### auth.ts
Contient :
```typescript
login()
logout()
getCurrentUser()
```
La logique auth du frontend est centralisée ici.

---

## 11.Dashboard
Page :
```text
DashboardPage
```
Charge :
```typescript
const currentUser = await getCurrentUser()
```
via :
```typescript
useEffect()
```
et stocke :
```typescript
const [user, setUser]
```

---

## 12. Gestion des rôles
Le user contient :
```typescript
roles: [
    {
        id: 1,
        name: "passenger"
    }
]
```
Bonne méthode :
```typescript
const isDriver = user.roles.some(role => role.name === "driver")
const isPassenger = user.roles.some(role => role.name === "passenger")
```
Pas de state dédié :
```typescript
setIsDriver()
setIsPassenger()
```
Les rôles sont calculés.

---

## 13. Structure Dashboard

Actuellement :
```text
DashboardPage
│
├── UserProfile
├── Participations
├── Cars
└── CarpoolsManager
```
Le user est chargé dans le parent.
Puis passé en props.
Les autres données métier restent chargées dans chaque composant.
Problème NavBar
Navbar avec :
```text
Connexion
Inscription
```
ou
```text
Déconnexion
```
selon l'état utilisateur.
Actuellement :
```text
F5 nécessaire
```
pour rafraîchir l'affichage.
Cause :
```text
Pas encore d'AuthContext
```
Décision :
```text
Reporter l'AuthContext plus tard
```
et continuer l'intégration.

---

## 14. Décision Architecture

Priorité actuelle :
```text
✅ Authentification
✅ Cookie HttpOnly
✅ Login
✅ GET /users/me
✅ Dashboard
⏳ Remplacer les mocks par les vraies données
⏳ Dashboard Driver
⏳ Dashboard Passenger
⏳ Dashboard Employee
⏳ Dashboard Admin
⏳ AuthContext
⏳ Autorisations fines
```

---

## 15. Philosophie retenue
Ne pas bloquer le projet avec les autorisations maintenant.
Faire :
```text
Frontend complet
  ↓
Données réelles
  ↓
Tests métier
  ↓
Puis autorisations
```
Autorisations prévues plus tard :
```python
require_authenticated()
require_employee()
require_admin()
```

---

## 16. Estimation actuelle
Évaluation réaliste :
```text
Fin septembre :
Application globalement utilisable

Mi-octobre :
Version fonctionnelle solide

Fin octobre :
Version présentable et stabilisée
```
La plus grosse difficulté (JWT + Front + Cookies HttpOnly + Communication Front/Back) est déjà passée.

💬 Quand tu ouvriras le nouveau topic, colle simplement ce résumé et ajoute :

"Nous continuons EcoRide à partir de ce contexte."

Et je pourrai repartir immédiatement sur les mêmes bases, sans que tu aies à tout réexpliquer.