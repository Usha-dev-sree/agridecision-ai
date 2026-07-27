// ============================================================
// AgriDecision AI — JanusGraph Property Graph Schema Setup
// Gremlin + Groovy Schema Initialization Script
// JanusGraph 1.0+ / TinkerPop 3.7+
// ============================================================
// Execution: Run inside JanusGraph Gremlin Server console
//   bin/gremlin.sh < database/janusgraph/003_janusgraph_schema.groovy
// ============================================================

// Open management transaction
mgmt = graph.openManagement()

// ────────────────────────────────────────────────────────────
// SECTION 1: PROPERTY KEYS
// ────────────────────────────────────────────────────────────

// --- Shared Properties ---
def propCode        = mgmt.makePropertyKey('code').dataType(String.class).cardinality(Cardinality.SINGLE).make()
def propName        = mgmt.makePropertyKey('name').dataType(String.class).cardinality(Cardinality.SINGLE).make()
def propDescription = mgmt.makePropertyKey('description').dataType(String.class).cardinality(Cardinality.SINGLE).make()
def propCategory    = mgmt.makePropertyKey('category').dataType(String.class).cardinality(Cardinality.SINGLE).make()
def propCreatedAt   = mgmt.makePropertyKey('createdAt').dataType(Date.class).cardinality(Cardinality.SINGLE).make()

// --- Crop Properties ---
def propCropCode         = mgmt.makePropertyKey('cropCode').dataType(String.class).cardinality(Cardinality.SINGLE).make()
def propVarietyCode      = mgmt.makePropertyKey('varietyCode').dataType(String.class).cardinality(Cardinality.SINGLE).make()
def propScientificName   = mgmt.makePropertyKey('scientificName').dataType(String.class).cardinality(Cardinality.SINGLE).make()
def propSeasonType       = mgmt.makePropertyKey('seasonType').dataType(String.class).cardinality(Cardinality.SINGLE).make()
def propDurationDays     = mgmt.makePropertyKey('durationDays').dataType(Integer.class).cardinality(Cardinality.SINGLE).make()
def propWaterReqMm       = mgmt.makePropertyKey('waterRequirementMm').dataType(Float.class).cardinality(Cardinality.SINGLE).make()
def propMspInr           = mgmt.makePropertyKey('mspInrPerQuintal').dataType(Float.class).cardinality(Cardinality.SINGLE).make()

// --- Pest/Disease Properties ---
def propPestCode         = mgmt.makePropertyKey('pestCode').dataType(String.class).cardinality(Cardinality.SINGLE).make()
def propSeverity         = mgmt.makePropertyKey('severity').dataType(String.class).cardinality(Cardinality.SINGLE).make()
def propSymptoms         = mgmt.makePropertyKey('symptoms').dataType(String.class).cardinality(Cardinality.SINGLE).make()
def propModelClassLabel  = mgmt.makePropertyKey('modelClassLabel').dataType(String.class).cardinality(Cardinality.SINGLE).make()

// --- Chemical/Input Properties ---
def propActiveIngredient = mgmt.makePropertyKey('activeIngredient').dataType(String.class).cardinality(Cardinality.SINGLE).make()
def propFormulation      = mgmt.makePropertyKey('formulation').dataType(String.class).cardinality(Cardinality.SINGLE).make()
def propDoseKgHa         = mgmt.makePropertyKey('doseKgHa').dataType(Float.class).cardinality(Cardinality.SINGLE).make()
def propWaitingPeriodDays= mgmt.makePropertyKey('waitingPeriodDays').dataType(Integer.class).cardinality(Cardinality.SINGLE).make()
def propIsOrganic        = mgmt.makePropertyKey('isOrganic').dataType(Boolean.class).cardinality(Cardinality.SINGLE).make()

// --- Soil Properties ---
def propTextureClass     = mgmt.makePropertyKey('textureClass').dataType(String.class).cardinality(Cardinality.SINGLE).make()
def propPhMin            = mgmt.makePropertyKey('phMin').dataType(Float.class).cardinality(Cardinality.SINGLE).make()
def propPhMax            = mgmt.makePropertyKey('phMax').dataType(Float.class).cardinality(Cardinality.SINGLE).make()
def propOrganicCarbonPct = mgmt.makePropertyKey('organicCarbonPct').dataType(Float.class).cardinality(Cardinality.SINGLE).make()

// --- AEZ Properties ---
def propZoneCode         = mgmt.makePropertyKey('zoneCode').dataType(String.class).cardinality(Cardinality.SINGLE).make()
def propRegion           = mgmt.makePropertyKey('region').dataType(String.class).cardinality(Cardinality.SINGLE).make()
def propRainfallAvgMm    = mgmt.makePropertyKey('rainfallAvgMm').dataType(Float.class).cardinality(Cardinality.SINGLE).make()

// --- Edge Properties ---
def propCompatibility    = mgmt.makePropertyKey('compatibility').dataType(String.class).cardinality(Cardinality.SINGLE).make()
def propConfidence       = mgmt.makePropertyKey('confidence').dataType(Float.class).cardinality(Cardinality.SINGLE).make()
def propBenefitType      = mgmt.makePropertyKey('benefitType').dataType(String.class).cardinality(Cardinality.SINGLE).make()
def propSourceReference  = mgmt.makePropertyKey('sourceReference').dataType(String.class).cardinality(Cardinality.SINGLE).make()

// ────────────────────────────────────────────────────────────
// SECTION 2: VERTEX LABELS
// ────────────────────────────────────────────────────────────

def vCropVariety     = mgmt.makeVertexLabel('CropVariety').make()
def vPestDisease     = mgmt.makeVertexLabel('PestDisease').make()
def vInputProduct    = mgmt.makeVertexLabel('InputProduct').make()
def vSoilType        = mgmt.makeVertexLabel('SoilType').make()
def vAEZone          = mgmt.makeVertexLabel('AgroEcologicalZone').make()
def vNutrientElement = mgmt.makeVertexLabel('NutrientElement').make()
def vCropFamily      = mgmt.makeVertexLabel('CropFamily').make()
def vGrowthStage     = mgmt.makeVertexLabel('CropGrowthStage').make()

// ────────────────────────────────────────────────────────────
// SECTION 3: EDGE LABELS
// ────────────────────────────────────────────────────────────

// Crop → Crop
def eSuitableForRotation  = mgmt.makeEdgeLabel('SUITABLE_FOR_ROTATION').multiplicity(MULTI).make()
def eIntercrops           = mgmt.makeEdgeLabel('INTERCROPS_WITH').multiplicity(MULTI).make()
def eCompetitesWith       = mgmt.makeEdgeLabel('COMPETES_WITH').multiplicity(MULTI).make()

// Pest → Crop
def eAffects              = mgmt.makeEdgeLabel('AFFECTS').multiplicity(MULTI).make()
def eSpreadsByVector      = mgmt.makeEdgeLabel('SPREADS_BY').multiplicity(MULTI).make()

// Input → Pest
def eControlls            = mgmt.makeEdgeLabel('CONTROLS').multiplicity(MULTI).make()
def eResistantTo          = mgmt.makeEdgeLabel('RESISTANT_TO').multiplicity(MULTI).make()

// Input → Crop
def eAppliedTo            = mgmt.makeEdgeLabel('APPLIED_TO').multiplicity(MULTI).make()
def ePhytotoxicTo         = mgmt.makeEdgeLabel('PHYTOTOXIC_TO').multiplicity(MULTI).make()

// Crop → Soil / AEZ
def eSuitableInSoil       = mgmt.makeEdgeLabel('SUITABLE_IN_SOIL').multiplicity(MULTI).make()
def eSuitableInAEZ        = mgmt.makeEdgeLabel('SUITABLE_IN_AEZ').multiplicity(MULTI).make()

// Crop → Nutrient
def eRequiresNutrient     = mgmt.makeEdgeLabel('REQUIRES_NUTRIENT').multiplicity(MULTI).make()
def eFixesNutrient        = mgmt.makeEdgeLabel('FIXES_NUTRIENT').multiplicity(MULTI).make()

// Crop → Growth Stage
def eHasGrowthStage       = mgmt.makeEdgeLabel('HAS_GROWTH_STAGE').multiplicity(MULTI).make()

// Pest → Pest (transmission)
def eAlternateHost        = mgmt.makeEdgeLabel('ALTERNATE_HOST_ON').multiplicity(MULTI).make()

// ────────────────────────────────────────────────────────────
// SECTION 4: COMPOSITE INDEXES (For fast vertex lookup)
// ────────────────────────────────────────────────────────────

// Unique crop variety index (for direct lookup)
mgmt.buildIndex('cropVarietyByCode', Vertex.class)
    .addKey(propVarietyCode)
    .indexOnly(vCropVariety)
    .unique()
    .buildCompositeIndex()

// Crop code index (for filtering all varieties of a crop)
mgmt.buildIndex('cropByCropCode', Vertex.class)
    .addKey(propCropCode)
    .indexOnly(vCropVariety)
    .buildCompositeIndex()

// Pest code unique index
mgmt.buildIndex('pestByCode', Vertex.class)
    .addKey(propPestCode)
    .indexOnly(vPestDisease)
    .unique()
    .buildCompositeIndex()

// AEZ zone code unique index
mgmt.buildIndex('aezByZoneCode', Vertex.class)
    .addKey(propZoneCode)
    .indexOnly(vAEZone)
    .unique()
    .buildCompositeIndex()

// Input product by code
mgmt.buildIndex('inputByCode', Vertex.class)
    .addKey(propCode)
    .indexOnly(vInputProduct)
    .unique()
    .buildCompositeIndex()

// ────────────────────────────────────────────────────────────
// SECTION 5: MIXED INDEXES (Elasticsearch-backed, for full-text)
// ────────────────────────────────────────────────────────────

// Full-text search on crop names and descriptions
mgmt.buildIndex('cropVarietySearch', Vertex.class)
    .addKey(propName, Mapping.TEXT.asParameter())
    .addKey(propScientificName, Mapping.TEXT.asParameter())
    .addKey(propSeasonType, Mapping.STRING.asParameter())
    .indexOnly(vCropVariety)
    .buildMixedIndex('search')

// Full-text search on pest/disease symptoms
mgmt.buildIndex('pestDiseaseSearch', Vertex.class)
    .addKey(propName, Mapping.TEXT.asParameter())
    .addKey(propSymptoms, Mapping.TEXT.asParameter())
    .addKey(propCategory, Mapping.STRING.asParameter())
    .indexOnly(vPestDisease)
    .buildMixedIndex('search')

// Commit schema changes
mgmt.commit()

println("JanusGraph schema committed successfully.")

// ────────────────────────────────────────────────────────────
// SECTION 6: AWAIT INDEX AVAILABILITY
// ────────────────────────────────────────────────────────────

ManagementSystem.awaitGraphIndexStatus(graph, 'cropVarietyByCode').call()
ManagementSystem.awaitGraphIndexStatus(graph, 'pestByCode').call()
ManagementSystem.awaitGraphIndexStatus(graph, 'aezByZoneCode').call()
ManagementSystem.awaitGraphIndexStatus(graph, 'cropVarietySearch').call()
ManagementSystem.awaitGraphIndexStatus(graph, 'pestDiseaseSearch').call()

// Reindex if needed (for existing data)
mgmt = graph.openManagement()
mgmt.updateIndex(mgmt.getGraphIndex('cropVarietySearch'), SchemaAction.REINDEX).get()
mgmt.commit()

println("All JanusGraph indexes are active and ready.")
