# User Manual
## AgriDecision AI — Farmer & Agronomist Usage Guide
**Version:** 1.0 | **Date:** July 28, 2026

---

## 1. Introduction

AgriDecision AI helps Indian farmers make data-driven decisions for crop selection, disease detection, market timing, and agricultural credit access. This manual covers usage of both the **Web Portal** (Agronomist Portal) and **Mobile Application** for Farmers, Agronomists, and Enterprise users.

---

## 2. Getting Started

### 2.1 Web Portal Access

1. Open your browser and navigate to: **https://app.agridecision.ai**
2. You will see the AgriDecision AI login page.

### 2.2 Mobile App Installation

- **Android:** Download from Google Play Store — search "AgriDecision AI"
- **iOS:** Download from Apple App Store — search "AgriDecision AI"

---

## 3. Account Registration

### 3.1 Phone OTP Registration

1. On the login screen, enter your **10-digit mobile number** with country code (+91)
2. Click **"Send OTP"** — you will receive a 6-digit OTP via SMS within 30 seconds
3. Enter the OTP in the verification box
4. Complete your profile:
   - Full Name
   - Role: Select **Farmer**, **Agronomist**, or **Enterprise**
   - State and District
5. Click **"Complete Registration"**

### 3.2 Google Sign-In

1. Click **"Sign in with Google"**
2. Select your Google account
3. On first login, complete your profile (name, role, state, district)

### 3.3 Setting Up Multi-Factor Authentication (MFA)

For enhanced security (recommended for Agronomists and Enterprise users):

1. Go to **Settings → Security → Enable MFA**
2. A QR code will appear — scan it with Google Authenticator or Authy
3. Enter the 6-digit code shown in your authenticator app
4. Click **"Verify & Enable MFA"**

From this point, MFA code will be required at every login.

---

## 4. Farmer Workflows

### 4.1 Adding Your First Farm Plot

1. Navigate to **My Farms** (left sidebar)
2. Click **"+ Add Farm Plot"**
3. Fill in the details:
   - **Plot Name:** e.g., "Ranga Reddy Plot 1"
   - **Total Area:** Enter area in hectares (e.g., 2.5)
   - **Irrigation Type:** Select RAINFED / CANAL / DRIP / SPRINKLER
4. To add the boundary:
   - Click **"Draw Boundary"** — the Leaflet map will open
   - Click on map corners to trace your farm boundary
   - Click **"Save Boundary"** when complete
   - The system will calculate the exact area automatically
5. Alternatively, use the **Mobile App → Maps screen** to walk your farm boundary using GPS

### 4.2 Uploading Soil Test Results

After receiving your soil test report from a lab:

1. Go to **My Farms → [Select Plot] → Soil Profile**
2. Click **"Update Soil Profile"**
3. Enter values from your soil test report:
   - **pH Level** (e.g., 6.8)
   - **Organic Carbon %** (e.g., 1.2)
   - **Nitrogen content** (kg/ha) — (e.g., 180)
   - **Phosphorus content** (kg/ha) — (e.g., 45)
   - **Potassium content** (kg/ha) — (e.g., 220)
   - **Electrical Conductivity** (dS/m) — (e.g., 0.35)
4. Click **"Save Soil Profile"**
5. The system validates your entries against agronomic bounds — any out-of-range values will show a warning

### 4.3 Getting Crop Recommendations

1. Navigate to **Advisory → Crop Recommendation**
2. Select your **farm plot** from the dropdown
3. The system automatically loads your soil profile
4. Click **"Get AI Recommendation"**
5. Results appear within 2 seconds:
   - **Recommended Crop** (e.g., Wheat) with confidence percentage
   - **Why this recommendation** — shows which soil factors drove the decision (bar chart)
   - **Alternate crops** with their suitability scores
6. Click **"View Full Explanation"** to see the detailed SHAP feature importance chart

### 4.4 Leaf Disease Detection

Using your smartphone (Mobile App):

1. Open the **AgriDecision AI** mobile app
2. Tap **"Disease Detection"** (camera icon)
3. Tap **"Take Photo"** and photograph an affected leaf (ensure good lighting, leaf fills frame)
4. Select the **crop type** from the dropdown (e.g., Wheat)
5. Tap **"Analyze Disease"**
6. Results appear within 5 seconds:
   - **Disease name** (e.g., "Leaf Rust") with confidence percentage
   - **Attention Map** — red areas show where the AI focused to detect the disease
   - **Treatment steps** — actionable remedy recommendations
   - **Warning signs** to watch for

Using the Web Portal:

1. Go to **Advisory → Disease Detection**
2. Click **"Upload Leaf Image"** and select a JPEG/PNG photo
3. Select crop type and click **"Detect Disease"**

### 4.5 Checking Weather Forecast

1. Navigate to **Weather** in the sidebar
2. Select your farm plot — the forecast loads automatically based on your plot's GPS location
3. You will see:
   - **7-day forecast cards**: temperature, rainfall, humidity
   - **Evapotranspiration (ET₀)**: how much water your soil will lose each day
   - **Agronomic alerts**: e.g., "Heavy rain expected — hold pesticide spray"
4. Tap any day for detailed hourly data

### 4.6 Market Price Intelligence

1. Navigate to **Market** in the sidebar
2. Select a commodity (e.g., Wheat)
3. View:
   - **Current Mandi prices** across your region
   - **7-day AI price forecast** with trend direction
   - **Best sale window** recommendation (when the model predicts peak prices)

### 4.7 Loan Application

1. Navigate to **Loans** in the sidebar
2. Click **"Apply for Agricultural Loan"**
3. Complete the application form:
   - Purpose (Crop Production / Equipment / Land Development)
   - Loan Amount (INR)
   - Collateral description
4. Click **"Check Eligibility"** to see your estimated credit score
5. Click **"Submit Application"** — you will receive an SMS confirmation
6. View **Government Schemes** you may be eligible for (e.g., PM-KISAN Credit Card)

---

## 5. Agronomist Workflows

### 5.1 Agronomist Dashboard

After logging in with an **Agronomist** role:

1. Your dashboard shows:
   - **Pending Reviews**: Recommendations awaiting your expert annotation
   - **Active Farmers**: Farmers in your assigned district
   - **Disease Alerts**: Recent high-severity disease detections
   - **Advisory Queue**: Unresolved farmer advisory queries

### 5.2 Reviewing AI Recommendations

1. Go to **Advisory → Pending Reviews**
2. Click on a recommendation to view:
   - Farmer's soil profile
   - AI-recommended crop with SHAP explanation
   - Historical recommendations for the same plot
3. Add your expert annotation:
   - Confirm or override the AI recommendation
   - Add a free-text advisory note
4. Click **"Submit Review"** — the farmer is notified via SMS

### 5.3 Creating Custom Advisory

1. Go to **Advisory → New Advisory**
2. Select farmer and farm plot
3. Type your advisory in the text field or use the **AI Advisory Query**:
   - Type a symptom/question (e.g., "yellow leaves on wheat after rain")
   - The AI returns diagnosis, treatment steps, and warning signs
4. Edit and finalize, then click **"Send Advisory"**

---

## 6. Enterprise User Workflows

### 6.1 Creating a Procurement Contract

1. Log in with **Enterprise** role
2. Navigate to **Contracts → New Contract**
3. Fill in:
   - Commodity (e.g., Wheat)
   - Quantity (metric tons)
   - Offered price (INR/quintal)
   - Delivery date
   - Delivery location
4. Link target farm plots:
   - Search by farmer name or farm ID
   - Add verified plots to the contract
5. Click **"Publish Contract"** — linked farmers receive notification

### 6.2 Supply Chain Traceability

1. Go to **Contracts → Active Contracts**
2. Click on a contract to see:
   - Linked farm plot GPS coordinates
   - Plot NDVI history (vegetation health over time)
   - Soil test reports
   - IoT sensor readings
   - Harvest progress notes from the farmer

---

## 7. Notifications

You will receive alerts via:
- **SMS:** Crop recommendation ready, disease alert, loan status update
- **Push Notification (mobile):** Weather advisory, price spike alert, contract offer
- **Email:** Weekly farm summary, monthly advisory report

To manage notification preferences:
1. Go to **Settings → Notifications**
2. Toggle individual notification types on/off per channel

---

## 8. Offline Mode (Mobile App)

The AgriDecision AI mobile app works offline for 72+ hours:

1. **Available offline:**
   - View your farm plots and soil profiles
   - Browse previously loaded weather forecasts
   - Review past disease detections and recommendations
   - Draft new advisory queries (sync when online)

2. **Automatic Sync:**
   - When internet connectivity is restored, the app automatically syncs offline data
   - A sync indicator appears in the top-right corner during background sync

---

## 9. Help & Support

| Channel | Contact |
| :--- | :--- |
| **In-App Chat** | Click the chat bubble icon (bottom-right) |
| **Kisan Helpline** | 1800-xxx-xxxx (Toll-free, 9 AM–6 PM IST) |
| **WhatsApp** | +91-XXXXXXXXXX |
| **Email** | support@agridecision.ai |
| **Documentation** | https://docs.agridecision.ai |
