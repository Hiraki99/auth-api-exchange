# Login-Python
- Install requirement:
```
    > pip install -r requirements.txt
```

- Config Project in config.py

- Generate DB
```
    > from yourapplication import db
    > db.create_all()
    > python3 manage db init
```
- For migrate database
```
    > python3 manage db migrate

    > python3 manage db upgrade
```
- Init Base Data for Project
```
    > python3 runPythonLogin.py --init
```
- start project
```
    > python3 runPythonLogin.py
```
