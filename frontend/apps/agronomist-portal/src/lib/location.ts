/**
 * AgriDecision AI - Robust Geolocation Utility
 * 3-tier strategy:
 *  1. Browser High-Accuracy GPS  → exact location (requires user permission)
 *  2. Browser Low-Accuracy Wi-Fi → rough city-level if GPS unavailable
 *  3. IP-based network fallback  → last resort
 */

export interface LocationResult {
  lat: number;
  lng: number;
  accuracy?: number;       // metres, if available
  label: string;
  isHighAccuracy: boolean;
  source: 'gps' | 'wifi' | 'ip' | 'default';
}

/**
 * Wraps navigator.geolocation.getCurrentPosition as a Promise.
 */
function getBrowserLocation(highAccuracy: boolean, timeoutMs: number): Promise<GeolocationPosition> {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation API not supported'));
      return;
    }
    navigator.geolocation.getCurrentPosition(resolve, reject, {
      enableHighAccuracy: highAccuracy,
      timeout: timeoutMs,
      maximumAge: 0,        // never use cached position for exact location
    });
  });
}

/**
 * Main entry point.
 * Requests the most precise location the device + browser can provide,
 * with automatic fallbacks so location is ALWAYS returned.
 */
export async function getAccurateLocation(): Promise<LocationResult> {

  // ── Tier 1: High-Accuracy GPS (asks browser permission, triggers dialog) ──
  try {
    const pos = await getBrowserLocation(true, 12000);
    const { latitude, longitude, accuracy } = pos.coords;
    return {
      lat: latitude,
      lng: longitude,
      accuracy,
      label: `📍 GPS Location (±${Math.round(accuracy ?? 0)} m)  ${latitude.toFixed(6)}°, ${longitude.toFixed(6)}°`,
      isHighAccuracy: true,
      source: 'gps',
    };
  } catch (err: any) {
    // PERMISSION_DENIED (code 1) — user blocked location; skip tier 2 browser attempt
    if (err?.code === 1) {
      console.warn('Location permission denied by user — falling back to IP geolocation.');
    } else {
      // TIMEOUT or POSITION_UNAVAILABLE — try low-accuracy Wi-Fi triangulation
      console.warn('High-accuracy GPS timed out / unavailable. Trying low-accuracy mode…', err?.message);

      // ── Tier 2: Low-Accuracy Wi-Fi / Network triangulation ──
      try {
        const pos = await getBrowserLocation(false, 6000);
        const { latitude, longitude, accuracy } = pos.coords;
        return {
          lat: latitude,
          lng: longitude,
          accuracy,
          label: `📶 Network Location (±${Math.round(accuracy ?? 0)} m)  ${latitude.toFixed(5)}°, ${longitude.toFixed(5)}°`,
          isHighAccuracy: false,
          source: 'wifi',
        };
      } catch (e2) {
        console.warn('Low-accuracy geolocation also failed. Falling back to IP…', e2);
      }
    }
  }

  // ── Tier 3a: IP Geolocation — ipwhois.app ──
  try {
    const res = await fetch('https://ipwhois.app/json/', { signal: AbortSignal.timeout(5000) });
    const data = await res.json();
    if (data?.latitude && data?.longitude) {
      const place = [data.city, data.region, data.country].filter(Boolean).join(', ');
      return {
        lat: Number(data.latitude),
        lng: Number(data.longitude),
        label: `🌐 IP Location: ${place}  (${Number(data.latitude).toFixed(4)}°, ${Number(data.longitude).toFixed(4)}°)`,
        isHighAccuracy: false,
        source: 'ip',
      };
    }
  } catch (e) {
    console.warn('ipwhois.app failed, trying ipapi.co…', e);
  }

  // ── Tier 3b: IP Geolocation — ipapi.co ──
  try {
    const res = await fetch('https://ipapi.co/json/', { signal: AbortSignal.timeout(5000) });
    const data = await res.json();
    if (data?.latitude && data?.longitude) {
      const place = [data.city, data.region, data.country_name].filter(Boolean).join(', ');
      return {
        lat: Number(data.latitude),
        lng: Number(data.longitude),
        label: `🌐 IP Location: ${place}  (${Number(data.latitude).toFixed(4)}°, ${Number(data.longitude).toFixed(4)}°)`,
        isHighAccuracy: false,
        source: 'ip',
      };
    }
  } catch (e) {
    console.warn('ipapi.co also failed.', e);
  }

  // ── Tier 4: Regional default (India center) ──
  return {
    lat: 20.5937,
    lng: 78.9629,
    label: '🗺️ Default: India Center (location access unavailable)',
    isHighAccuracy: false,
    source: 'default',
  };
}
