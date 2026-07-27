// ─── Auth Types ───────────────────────────────────────────────────────────────
export interface LoginRequest {
  phone_number: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface User {
  id: string;
  full_name: string;
  phone_number: string;
  email: string | null;
  role: 'FARMER' | 'AGRONOMIST' | 'ADMIN' | 'ENTERPRISE';
  account_status: 'ACTIVE' | 'INACTIVE' | 'SUSPENDED' | 'PENDING_VERIFICATION';
  has_verified_phone: boolean;
  has_verified_agronomist_credential: boolean;
  preferred_language: string;
  state_code: string;
  district_name: string | null;
  farmer_type: string | null;
  referral_code: string | null;
  created_at: string;
  updated_at: string;
  profile: UserProfile | null;
}

export interface UserProfile {
  id: string;
  user_id: string;
  avatar_url: string | null;
  bio: string | null;
  land_holding_ha: number | null;
  years_of_farming: number | null;
  education_level: string | null;
  agronomist_reg_no: string | null;
  agronomist_state: string | null;
  agronomist_verified_at: string | null;
  created_at: string;
  updated_at: string;
}

// ─── Farm Types ───────────────────────────────────────────────────────────────
export interface FarmPlot {
  id: string;
  owner_id: string;
  name: string;
  total_area_ha: number;
  irrigation_type: 'RAINFED' | 'IRRIGATED' | 'MICRO_IRRIGATED';
  is_active: boolean;
  centroid_lat: number | null;
  centroid_lng: number | null;
  created_at: string;
  updated_at: string;
  boundary?: PlotBoundary;
  soil_profile?: SoilProfile;
}

export interface PlotBoundary {
  plot_id: string;
  geojson: GeoJSON.Geometry;
  perimeter_km: number | null;
  elevation_m: number | null;
}

export interface SoilProfile {
  plot_id: string;
  soil_type: string | null;
  texture_class: string | null;
  ph_level: number | null;
  organic_carbon_percent: number | null;
  nitrogen_content: number | null;
  phosphorus_content: number | null;
  potassium_content: number | null;
  bulk_density: number | null;
  source: string;
  last_tested_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface CropSeason {
  id: string;
  plot_id: string;
  crop_name: string;
  season_name: 'KHARIF' | 'RABI' | 'ZAID';
  sowing_date: string | null;
  expected_harvest_date: string | null;
  actual_harvest_date: string | null;
  sown_area_ha: number | null;
  seed_variety: string | null;
  status: 'PLANNED' | 'SOWN' | 'GROWING' | 'HARVESTED' | 'FAILED';
  notes: string | null;
  created_at: string;
}

export interface IoTDevice {
  id: string;
  plot_id: string;
  device_serial: string;
  device_type: 'SOIL_SENSOR' | 'WEATHER_STATION' | 'IRRIGATION_CONTROLLER' | 'CAMERA';
  is_active: boolean;
  last_seen_at: string | null;
  firmware_version: string | null;
  battery_level: number | null;
  created_at: string;
}

// ─── Advisory / AI Types ──────────────────────────────────────────────────────
export interface RecommendedCrop {
  crop_name: string;
  confidence_score: number;
  expected_yield_kg_ha: number | null;
  suitability_reason: string | null;
}

export interface CropRecommendation {
  id: string;
  plot_id: string;
  user_id: string;
  model_version: string;
  season_name: string;
  top_confidence_score: number | null;
  recommendations: RecommendedCrop[];
  input_features: Record<string, unknown> | null;
  created_at: string;
}

export interface DiseaseDetectionResult {
  predicted_class: string;
  confidence_score: number;
  all_probabilities: Record<string, number>;
  focus_attention_center: { x: number; y: number };
  grad_cam_heatmap_sample: number[][];
}

export interface YieldPrediction {
  plot_id: string;
  crop_name: string;
  expected_yield_kg_ha: number;
  explanations: Record<string, number>;
}

export interface PriceForecast {
  crop_name: string;
  market_id: string;
  current_price: number;
  forecast_next_7_days: number[];
}

// ─── Weather Types ────────────────────────────────────────────────────────────
export interface WeatherForecast {
  date: string;
  temp_max_c: number | null;
  temp_min_c: number | null;
  precipitation_mm: number | null;
  windspeed_max_kmh: number | null;
  solar_radiation_mj_m2: number | null;
  eto_fao_mm_day: number | null;
}

// ─── Market Types ─────────────────────────────────────────────────────────────
export interface MarketPrice {
  crop_name: string;
  market_name: string;
  state: string;
  modal_price: number;
  min_price: number;
  max_price: number;
  arrival_date: string;
  unit: string;
}

// ─── Diagnosis Types ──────────────────────────────────────────────────────────
export interface Diagnosis {
  id: string;
  plot_id: string;
  user_id: string;
  image_url: string | null;
  disease_name: string | null;
  confidence_score: number | null;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' | null;
  treatment_suggestion: string | null;
  created_at: string;
}

export interface IrrigationSchedule {
  id: string;
  plot_id: string;
  crop_name: string;
  scheduled_date: string;
  water_requirement_mm: number;
  et0_mm_day: number;
  kc_factor: number;
  status: 'PENDING' | 'APPLIED' | 'SKIPPED';
}

// ─── Prompt Engine Types ──────────────────────────────────────────────────────
export interface AdvisoryResponse {
  diagnosis: string;
  remedy_steps: string[];
  warning_signs: string[];
  crop_suitability: Array<{
    crop_name: string;
    suitability_score: number;
    reason: string;
  }>;
}

// ─── API Common ───────────────────────────────────────────────────────────────
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface ApiError {
  type: string;
  title: string;
  detail: string;
  status: number;
}

// ─── Dashboard Types ──────────────────────────────────────────────────────────
export interface DashboardStats {
  total_plots: number;
  active_seasons: number;
  active_devices: number;
  pending_recommendations: number;
  total_area_ha: number;
}
