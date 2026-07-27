import { advisoryApi, aiApi, weatherApi, marketApi } from '@/lib/apiClient';
import type {
  CropRecommendation,
  Diagnosis,
  IrrigationSchedule,
  WeatherForecast,
  MarketPrice,
  YieldPrediction,
  PriceForecast,
  DiseaseDetectionResult,
  AdvisoryResponse,
} from '@/types';

export const advisoryService = {
  // Crop Recommendations
  getRecommendation: async (plotId: string, seasonName: string): Promise<CropRecommendation> => {
    const res = await advisoryApi.post<CropRecommendation>('/v1/advisory/recommendations', {
      plot_id: plotId,
      season_name: seasonName,
    });
    return res.data;
  },

  getRecommendationHistory: async (plotId: string): Promise<CropRecommendation[]> => {
    const res = await advisoryApi.get<CropRecommendation[]>(
      `/v1/advisory/recommendations/plots/${plotId}/history`
    );
    return res.data;
  },

  // Disease Diagnosis
  getDiagnoses: async (plotId: string): Promise<Diagnosis[]> => {
    const res = await advisoryApi.get<Diagnosis[]>(`/v1/advisory/diagnosis?plot_id=${plotId}`);
    return res.data;
  },

  detectDisease: async (imageFile: File): Promise<DiseaseDetectionResult> => {
    const formData = new FormData();
    formData.append('file', imageFile);
    const res = await aiApi.post<DiseaseDetectionResult>('/v1/detect-disease', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  // Irrigation
  getIrrigationSchedule: async (plotId: string): Promise<IrrigationSchedule[]> => {
    const res = await advisoryApi.get<IrrigationSchedule[]>(
      `/v1/advisory/irrigation?plot_id=${plotId}`
    );
    return res.data;
  },

  // Yield Prediction
  predictYield: async (plotId: string, cropName: string): Promise<YieldPrediction> => {
    const res = await aiApi.post<YieldPrediction>('/v1/predict-yield', {
      plot_id: plotId,
      crop_name: cropName,
      season_name: 'KHARIF',
    });
    return res.data;
  },

  // Price Forecast
  forecastPrice: async (cropName: string, marketId: string): Promise<PriceForecast> => {
    const res = await aiApi.post<PriceForecast>('/v1/forecast-price', {
      crop_name: cropName,
      market_id: marketId,
    });
    return res.data;
  },

  // LLM Advisory
  getAIAdvisory: async (query: string, plotId: string): Promise<AdvisoryResponse> => {
    const res = await aiApi.post<AdvisoryResponse>('/v1/advisory/query', {
      query,
      plot_id: plotId,
    });
    return res.data;
  },
};

export const weatherService = {
  getForecast: async (lat: number, lon: number, days = 7): Promise<WeatherForecast[]> => {
    const res = await weatherApi.get<WeatherForecast[]>('/v1/weather/forecast', {
      params: { lat, lon, forecast_days: days },
    });
    return res.data;
  },
};

export const marketService = {
  getPrices: async (cropName?: string, state?: string): Promise<MarketPrice[]> => {
    const res = await marketApi.get<MarketPrice[]>('/v1/market/prices', {
      params: { crop_name: cropName, state },
    });
    return res.data;
  },
};
