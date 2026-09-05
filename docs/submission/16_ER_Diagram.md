# Entity-Relationship (ER) Diagram
## AgriDecision AI — Relational Schema & Property Graph Data Model
**Document Version:** 1.0 | **Date:** July 28, 2026

---

## 1. Relational Database ER Diagram (PostgreSQL)

```mermaid
erDiagram
    IAM_USER ||--o{ FARM_PLOT : "owns"
    IAM_USER ||--o{ USER_SESSION : "has"
    IAM_USER ||--o{ AUDIT_LOG : "generates"
    IAM_USER ||--o{ SUBSCRIPTION : "subscribes"
    IAM_USER ||--o{ RECOMMENDATION : "requests"
    IAM_USER ||--o{ DISEASE_SCAN : "scans"
    IAM_USER ||--o{ LOAN_APPLICATION : "applies"

    FARM_PLOT ||--|| PLOT_BOUNDARY : "has_boundary"
    FARM_PLOT ||--|| SOIL_PROFILE : "has_soil"
    FARM_PLOT ||--o{ CROP_SEASON : "grows"
    FARM_PLOT ||--o{ IOT_DEVICE : "deploys"
    FARM_PLOT ||--o{ RECOMMENDATION : "evaluated_in"

    LOAN_APPLICATION ||--|| CREDIT_ASSESSMENT : "assessed_by"

    CONTRACT ||--o{ CONTRACT_PLOTS : "includes"
    FARM_PLOT ||--o{ CONTRACT_PLOTS : "contracted_in"

    IAM_USER {
        uuid id PK
        string phone_number UK
        string email UK
        string full_name
        enum role
        string state
        string district
        boolean is_active
        timestamp created_at
    }

    FARM_PLOT {
        uuid id PK
        uuid owner_id FK
        string name
        numeric total_area_ha
        string irrigation_type
        numeric centroid_lat
        numeric centroid_lng
        timestamp created_at
    }

    PLOT_BOUNDARY {
        uuid id PK
        uuid plot_id FK
        jsonb geojson
        geometry geom
        numeric area_ha
    }

    SOIL_PROFILE {
        uuid id PK
        uuid plot_id FK
        numeric ph_level
        numeric organic_carbon_pct
        numeric nitrogen_content
        numeric phosphorus_content
        numeric potassium_content
        numeric electrical_conductivity
        string texture_class
        timestamp sampled_at
    }

    RECOMMENDATION {
        uuid id PK
        uuid user_id FK
        uuid plot_id FK
        string model_version
        string recommended_crop
        numeric confidence_score
        jsonb shap_values
        boolean fallback_used
        timestamp created_at
    }

    DISEASE_SCAN {
        uuid id PK
        uuid user_id FK
        string image_s3_key
        string diagnosis_label
        numeric confidence
        string gradcam_s3_key
        timestamp created_at
    }

    LOAN_APPLICATION {
        uuid id PK
        uuid user_id FK
        numeric amount_inr
        string purpose
        integer credit_score
        string status
        timestamp applied_at
    }
```

---

## 2. JanusGraph Knowledge Graph Schema Diagram

```mermaid
graph LR
    Crop(("Crop Vertex<br/>(code, name, waterReq)"))
    Disease(("Disease Vertex<br/>(code, name, severity)"))
    Pest(("Pest Vertex<br/>(pestCode, name)"))
    Chemical(("Chemical Vertex<br/>(code, activeIngredient)"))
    Soil(("SoilProfile Vertex<br/>(textureClass, phMin)"))
    AEZ(("AgroEcoZone Vertex<br/>(zoneCode, region)"))

    Crop -- "SUSCEPTIBLE_TO" --> Disease
    Crop -- "SUSCEPTIBLE_TO" --> Pest
    Chemical -- "TREATS" --> Disease
    Chemical -- "TREATS" --> Pest
    Crop -- "GROWS_BEST_IN" --> Soil
    AEZ -- "AFFECTS" --> Crop
    Crop -- "COMPATIBLE_WITH" --> Crop
```
