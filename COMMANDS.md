# Management Commands

This document lists the custom management commands available for managing tenants and users in the EduERP system.

## Tenant Management

### Load Tenants
Creates or updates tenants based on the JSON configuration file.

**Command:**
```bash
python manage.py load_tenants




================================================================================
TENANT DATABASE REPORT
================================================================================
Total Created: 7
Total Updated: 1
Total Tenants: 8
--------------------------------------------------------------------------------
Schema               | Name                           | Domain                    | Status
--------------------------------------------------------------------------------
bishop_bangalore     | Bishop Cotton School           | bishopcotton.localhost    | active
dav_mumbai           | DAV Public School              | davmumbai.localhost       | trial
delhi_public         | Delhi Public School            | dpsrkp.localhost          | active    
--------------------------------------------------------------------------------
Schema               | Name                           | Domain                    | Status
--------------------------------------------------------------------------------
bishop_bangalore     | Bishop Cotton School           | bishopcotton.localhost    | active
dav_mumbai           | DAV Public School              | davmumbai.localhost       | trial
delhi_public         | Delhi Public School            | dpsrkp.localhost          | active
Schema               | Name                           | Domain                    | Status
--------------------------------------------------------------------------------
bishop_bangalore     | Bishop Cotton School           | bishopcotton.localhost    | active
dav_mumbai           | DAV Public School              | davmumbai.localhost       | trial
delhi_public         | Delhi Public School            | dpsrkp.localhost          | active
bishop_bangalore     | Bishop Cotton School           | bishopcotton.localhost    | active
dav_mumbai           | DAV Public School              | davmumbai.localhost       | trial
delhi_public         | Delhi Public School            | dpsrkp.localhost          | active
delhi_public         | Delhi Public School            | dpsrkp.localhost          | active
dps_kolkata          | Delhi Public School            | dpskolkata.localhost      | active
kendriya             | Kendriya Vidyalaya             | kvd1delhi.localhost       | active
public               | System Tenant                  | localhost                 | active
sanskriti_ahmedabad  | Sanskriti School               | sanskritiahmedabad.localhost | trial        
srm_chennai          | SRM Public School              | srmpschennai.localhost    | trial
--------------------------------------------------------------------------------
```

**Data File:**
`apps/tenants/data/tenants.json`

**Features:**
- Creates new tenants if they don't exist.
- Updates existing tenants with new data from the JSON file.
- Displays a detailed report of all tenants in the database.

**Example Data Format:**
```json
[
    {
        "schema_name": "public",
        "name": "System Tenant",
        "domain": "localhost",
        ...
    }
]
```

---

## User Management

### Create Tenant Superusers (Bulk)
Creates or updates superusers for tenants based on the JSON configuration file.

**Command:**
```bash
python manage.py create_tenant_superusers
```

**Data File:**
`apps/users/data/users.json`

**Features:**
- Creates superusers for specific tenants defined in the JSON.
- Updates existing users if they match the email.
- Handles tenant context switching automatically.

**Example Data Format:**
```json
[
    {
        "schema_name": "school_a",
        "users": [
            {
                "email": "admin@school.edu",
                "password": "password123",
                "role": "admin"
            }
        ]
    }
]
```

### Create Custom Superuser (CLI)
Creates a single superuser for a specific tenant using command-line arguments.

**Command:**
```bash
python manage.py create_custom_superuser --target-schema dps_kolkata --user-email admin@dps.edu --user-password admin@123


python manage.py create_staff_user --target-schema dps_kolkata --user-email=staff@example.com --user-password=password123

 

# Run complete setup
python manage.py setup_system

# Run with options
python manage.py setup_system --skip-migrations --force

# Run individual components
python manage.py setup_database
python manage.py setup_permissions_only
python manage.py setup_tenants --create-default

# Check setup status
python manage.py check --deploy

```


**Arguments:**
- `--target-schema`: The schema name of the tenant (e.g., `school_a`).
- `--user-email`: The email address of the user.
- `--user-password`: The password for the user.
- `--first_name`: (Optional) First name (default: 'Super').
- `--last_name`: (Optional) Last name (default: 'Admin').

**Example:**
```bash
python manage.py create_custom_superuser --target-schema school_a --user-email newadmin@springfield.edu --user-password SecurePass123!
python manage.py create_custom_superuser --target-schema school_a --user-email newadmin@springfield.edu --user-password SecurePass123!
```
