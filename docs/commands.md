# Commands used in the project

## 1. Python
install python package :
```shell
pip install pyjwt
```
Add requirements.txt package installed :
```shell
pip freeze > requirements.txt
```
Install dependants packages :
```shell
pip install -r requirements.txt
```

## 2. FastAPI
Start the server :
```shell
uvicorn app.main:app --reload
```

---

## 3. Linux / shell
Create folder tree structure :
```shell
mkdir -p app/services
```
Create file :
```shell
touch auth_service.py
```
Lister :
```shell
ls -la
```

---

## 4. security / JWT
Create random key hex
```shell
openssl rand -hex 32
```

---

## 5. Git
Initialisation :
```shell
git init
```
### Commit
add all files
```shell
git add .
```
or add few file:
```shell
git add app/schemas/authentication_schema.py
```
```shell
git commit -m'feat:add authentication module'
```
History :
```shell
git log --oneline
```

Create and switch to this branch :
```shell
git switch -c feature/authentication
```

check files to commit :
```shell
git status
```

---

## 6. PostgreSQL
psql -U postgres