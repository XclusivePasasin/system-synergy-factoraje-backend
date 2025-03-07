# synergy-factoraje-backend
Factoring is a financial service that allows suppliers to receive advance payments on their outstanding invoices in exchange for an agreed discount. This system facilitates cash flow for suppliers by advancing the payment of their accounts receivable without waiting for established deadlines.

## Installation of dependencies
In order to install the project, we will create a .venv to install the dependencies

### install virtualenv
```bash
  pip install virtualenv
```
### In case of error in the installation of virtualenv
```bash
  Set-ExecutionPolicy Bypass -Scope Process
```

### Create a virtual environment
```bash
  python -m venv venv
```

### Activate the virtual environment
```bash
  .\venv\Scripts\activate  
```

### Install the dependencies
```bash
  pip install -r requirements.txt
```

### Deactivate the virtual environment
```bash
  deactivate 
```

## Migrations of the database
if you want to create a migration, you must run the following commands

### Create a migration
```bash
  flask db init
```

```bash
  flask db migrate
```

### Run migrations
```bash
  flask db upgrade
```

## Migrations Seed
if you want to create a seed, you must run the following commands

### Create a seeds
```bash
  flask seed parametros
  flask seed estados
  flask seed roles
  flask seed menus
  flask seed proveedores
  flask seed facturas
  flask seed usuarios
  flask seed permisos

  flask seed parametros && flask seed estados && seed roles && flask seed menus && flask seed proveedores && flask seed facturas && flask seed usuarios && flask seed permisos
```

