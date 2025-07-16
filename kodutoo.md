# Kodutöö: võrgu halduse REST API

Arendada Python keeles REST API võrgu halduse lahendus VLAN halduseks koos CI/CD pipeline-iga ja Kubernetes paigaldusega.

## Nõuded

### 1. Repositoorium + dokumentatsioon

- GitHub või Bitbucket repositoorium
- **README.md** projekti seadistamise ja käivitamise juhised
- Korrektne .gitignore Python projektile

### 2. API disain

#### OpenAPI spetsifikatsioon

Luua **openapi.yml** fail, mis defineerib:

- **VLAN mudeli** skeema: ID, nimi, VLAN ID (1-4094), subnet (CIDR), gateway IP, status
- **API endpoint-id** koos request/response mudelitega
- **Veatöötluse** skeemad (4xx, 5xx vastused)

#### Implementeeritavad endpoint-id

```
# VLAN haldus
GET    /api/v1/vlans          - kõikide VLAN-ide loend
POST   /api/v1/vlans          - uue VLAN-i loomine
GET    /api/v1/vlans/{id}     - konkreetse VLAN-i andmed
PUT    /api/v1/vlans/{id}     - VLAN-i andmete uuendamine
DELETE /api/v1/vlans/{id}     - VLAN-i kustutamine

# Monitoorimine
GET    /health                - rakenduse tervisekontroll
```

**Workflow:** Esiteks disainida OpenAPI.yml → seejärel implementeerida Python-is vastavalt spetsifikatsioonile

### 3. Python implementatsioon

**Tehnoloogia:**

- **Python 3** keeles
- HTTP server 

**Implementeerida:**

- **6 REST endpoint-i** vastavalt OpenAPI spetsifikatsioonile (5 VLAN + 1 health)
- **JSON faili** salvestus/lugemine (vlans.json andmete hoidmiseks)
- **Input validatsioon** (VLAN ID vahemik, IP vormingud)
- **Veatöötlus** korrektne HTTP staatuskoodidega (200, 201, 400, 404, 500)

### 4. Testimine

- **Testid peavad katma kogu API funktsionaalsuse** (kõik VLAN CRUD operatsioonid + health endpoint)
- Testimine: unit, integration või mõlemad (kandidaadi valik)
- **Minimaalne koodikatvus: 70%**
- Testimise strateegia selgitamine README.md failis

### 5. CI/CD Pipeline

**Luua:** `.github/workflows/` või `bitbucket-pipelines.yml` fail

**Stage-id:**

1. **Test stage:** käivitab testid ja kontrollib koodikatvust (min 70%)
2. **Docker stage:** ehitab Docker image ja pushib registry-sse (Docker Hub või muu)
3. **Deploy stage:** uuendab Kubernetes deployment-i uue image-ga

**Nõue:** Pipeline peab ebaõnnestuma kui testid või build failivad

### 6. Kubernetes

**Luua YAML failid:**

- **`deployment.yaml`** - rakenduse paigaldamine (replicas, resources, health checks)
- **`service.yaml`** - teenuse eksportimine (ClusterIP või LoadBalancer)

**Nõuded:**

- Health check endpoint `/health` liveness/readiness probe-ideks
- Ressursside limiidid (CPU, memory) deployment-is
- Image viide pipeline-ist tuleva registry image-le

## Esitada

1. **Repositooriumi link** kus sisaldab:
   - **Kogu rakenduse kood** (Python lähtekood)
   - **openapi.yml** API spetsifikatsiooniga
   - Toimiv CI/CD pipeline (.github/workflows/ või bitbucket-pipelines.yml)
   - **Test coverage fail** (coverage.html, coverage.out või sarnane)
   - Pipeline käivitamise ajalugu (successful builds)
   - README.md projekti käivitamise juhised
