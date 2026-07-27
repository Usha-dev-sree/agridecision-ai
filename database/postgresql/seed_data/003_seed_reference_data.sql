-- ============================================================
-- AgriDecision AI — Seed Data: Reference Tables
-- Run AFTER 001_master_schema.sql
-- ============================================================

-- ────────────────────────────────────────────────────────────
-- 1. AGRO-ECOLOGICAL ZONES (15 major Indian zones)
-- ────────────────────────────────────────────────────────────
INSERT INTO reference.agro_ecological_zone (zone_code, zone_name, region, state_codes, rainfall_mm_avg, temp_avg_c, soil_types) VALUES
('AEZ_01', 'Western Himalayan Region',       'North',     ARRAY['HP','UK','JK'],          1200.00, 12.50, ARRAY['LOAM','SANDY_LOAM']),
('AEZ_02', 'Eastern Himalayan Region',        'Northeast', ARRAY['SK','AR','NL','MN','MZ','TR','ML'], 2500.00, 18.00, ARRAY['LOAM','CLAY_LOAM']),
('AEZ_03', 'Indo-Gangetic Plains (Upper)',     'North',     ARRAY['PB','HR','DL'],          750.00,  24.00, ARRAY['LOAM','SILT_LOAM','SANDY_LOAM']),
('AEZ_04', 'Indo-Gangetic Plains (Middle)',    'North',     ARRAY['UP'],                    900.00,  25.50, ARRAY['LOAM','SILT_LOAM','CLAY_LOAM']),
('AEZ_05', 'Indo-Gangetic Plains (Lower)',     'East',      ARRAY['BR','WB'],               1200.00, 26.00, ARRAY['SILT_LOAM','CLAY','LOAM']),
('AEZ_06', 'Central Highlands (Malwa)',        'Central',   ARRAY['MP','RJ'],               850.00,  25.00, ARRAY['CLAY','CLAY_LOAM']),
('AEZ_07', 'Deccan Plateau (North)',           'West',      ARRAY['MH','KA'],               700.00,  27.00, ARRAY['CLAY','CLAY_LOAM','LOAM']),
('AEZ_08', 'Deccan Plateau (South)',           'South',     ARRAY['KA','TN','AP'],           650.00,  28.00, ARRAY['SANDY_LOAM','LOAM','CLAY']),
('AEZ_09', 'Western Ghats & Coastal (West)',   'West',      ARRAY['KL','KA','MH','GA'],     3000.00, 26.50, ARRAY['CLAY_LOAM','LOAM','SANDY_CLAY_LOAM']),
('AEZ_10', 'Eastern Ghats & Coastal (East)',   'East',      ARRAY['AP','TN','OD'],           1100.00, 28.50, ARRAY['SANDY_LOAM','LOAM','CLAY']),
('AEZ_11', 'Gujarat Plains & Hills',           'West',      ARRAY['GJ'],                    800.00,  27.50, ARRAY['SANDY','LOAMY_SAND','SANDY_LOAM']),
('AEZ_12', 'Western Dry Region (Thar)',         'West',      ARRAY['RJ'],                    350.00,  28.00, ARRAY['SANDY','LOAMY_SAND']),
('AEZ_13', 'Eastern Plateau (Chhattisgarh)',   'Central',   ARRAY['CG','JH','OD'],           1400.00, 26.00, ARRAY['CLAY_LOAM','LOAM','SANDY_CLAY_LOAM']),
('AEZ_14', 'Bengal-Assam Plains',              'East',      ARRAY['WB','AS'],                1800.00, 26.00, ARRAY['SILT_LOAM','CLAY','LOAM']),
('AEZ_15', 'Islands Region',                   'Islands',   ARRAY['AN','LD'],                3000.00, 27.00, ARRAY['SANDY_LOAM','CLAY_LOAM'])
ON CONFLICT (zone_code) DO NOTHING;


-- ────────────────────────────────────────────────────────────
-- 2. CROP VARIETIES (30+ major Indian crops)
-- ────────────────────────────────────────────────────────────
INSERT INTO reference.crop_variety (crop_code, variety_code, common_name, scientific_name, local_names, season, duration_days_min, duration_days_max, water_requirement_mm, nitrogen_kg_per_ha, phosphorus_kg_per_ha, potassium_kg_per_ha, suitable_aez_codes, ph_min, ph_max, government_notified, msp_inr_per_quintal) VALUES
-- Rice varieties
('ORYZA_SATIVA', 'PUSA_BASMATI_1121', 'Pusa Basmati 1121', 'Oryza sativa L.', '{"hi":"पूसा बासमती 1121","pa":"ਪੂਸਾ ਬਾਸਮਤੀ 1121"}', 'KHARIF', 130, 150, 1200.00, 120.00, 60.00, 60.00, ARRAY['AEZ_03','AEZ_04'], 6.00, 7.50, TRUE, 2183.00),
('ORYZA_SATIVA', 'IR_64', 'IR-64', 'Oryza sativa L.', '{"hi":"आईआर-64","te":"ఐఆర్-64"}', 'KHARIF', 110, 125, 1100.00, 100.00, 50.00, 50.00, ARRAY['AEZ_04','AEZ_05','AEZ_10'], 5.50, 7.00, TRUE, 2183.00),
('ORYZA_SATIVA', 'SWARNA_MTU_7029', 'Swarna (MTU 7029)', 'Oryza sativa L.', '{"hi":"स्वर्णा","bn":"স্বর্ণা","or":"ସ୍ୱର୍ଣ୍ଣା"}', 'KHARIF', 140, 155, 1250.00, 110.00, 55.00, 55.00, ARRAY['AEZ_05','AEZ_13','AEZ_14'], 5.50, 7.50, TRUE, 2183.00),
('ORYZA_SATIVA', 'SAMBA_MAHSURI', 'Samba Mahsuri (BPT 5204)', 'Oryza sativa L.', '{"te":"సాంబ మసూరి","ta":"சம்பா மசூரி"}', 'KHARIF', 145, 160, 1300.00, 120.00, 60.00, 40.00, ARRAY['AEZ_08','AEZ_10'], 6.00, 7.50, TRUE, 2183.00),

-- Wheat varieties
('TRITICUM_AESTIVUM', 'HD_3086', 'HD 3086', 'Triticum aestivum L.', '{"hi":"एचडी 3086","pa":"ਐੱਚਡੀ 3086"}', 'RABI', 140, 155, 450.00, 150.00, 60.00, 40.00, ARRAY['AEZ_03','AEZ_04'], 6.00, 7.50, TRUE, 2275.00),
('TRITICUM_AESTIVUM', 'PBW_343', 'PBW 343', 'Triticum aestivum L.', '{"hi":"पीबीडब्ल्यू 343","pa":"ਪੀਬੀਡਬਲਿਊ 343"}', 'RABI', 135, 145, 400.00, 120.00, 60.00, 40.00, ARRAY['AEZ_03','AEZ_04','AEZ_06'], 6.50, 8.00, TRUE, 2275.00),
('TRITICUM_AESTIVUM', 'DBW_187', 'DBW 187 (Karan Vandana)', 'Triticum aestivum L.', '{"hi":"करण वंदना"}', 'RABI', 120, 135, 380.00, 140.00, 60.00, 40.00, ARRAY['AEZ_03','AEZ_04'], 6.00, 8.00, TRUE, 2275.00),

-- Maize varieties
('ZEA_MAYS', 'DKC_9144', 'DKC 9144 (Dekalb Hybrid)', 'Zea mays L.', '{"hi":"मक्का डीकेसी 9144","mr":"मका"}', 'KHARIF', 95, 110, 500.00, 120.00, 60.00, 40.00, ARRAY['AEZ_03','AEZ_04','AEZ_06','AEZ_07'], 5.50, 7.50, FALSE, 2090.00),
('ZEA_MAYS', 'HQPM_1', 'HQPM-1 (Quality Protein Maize)', 'Zea mays L.', '{"hi":"एचक्यूपीएम-1"}', 'KHARIF', 85, 100, 450.00, 100.00, 50.00, 40.00, ARRAY['AEZ_04','AEZ_06'], 5.50, 7.50, TRUE, 2090.00),

-- Soybean
('GLYCINE_MAX', 'JS_9560', 'JS 9560', 'Glycine max (L.) Merr.', '{"hi":"सोयाबीन जेएस 9560","mr":"सोयाबीन"}', 'KHARIF', 95, 110, 450.00, 30.00, 60.00, 40.00, ARRAY['AEZ_06','AEZ_07'], 6.00, 7.50, TRUE, 4600.00),

-- Cotton
('GOSSYPIUM', 'BUNNY_BG_II', 'Bunny Bt (BG-II)', 'Gossypium hirsutum L.', '{"hi":"बन्नी बीटी","te":"బన్ని బీటీ","gu":"બન્ની બીટી"}', 'KHARIF', 150, 180, 700.00, 120.00, 60.00, 60.00, ARRAY['AEZ_07','AEZ_08','AEZ_11'], 6.00, 8.00, TRUE, 6620.00),

-- Sugarcane
('SACCHARUM', 'CO_0238', 'CO 0238', 'Saccharum officinarum L.', '{"hi":"गन्ना सीओ 0238","mr":"ऊस"}', 'ANNUAL', 300, 365, 2000.00, 250.00, 100.00, 100.00, ARRAY['AEZ_04','AEZ_05'], 6.00, 8.00, TRUE, 315.00),

-- Mustard
('BRASSICA_JUNCEA', 'PUSA_BOLD', 'Pusa Bold', 'Brassica juncea (L.) Czern.', '{"hi":"सरसों पूसा बोल्ड","pa":"ਸਰ੍ਹੋਂ"}', 'RABI', 110, 130, 250.00, 80.00, 40.00, 40.00, ARRAY['AEZ_03','AEZ_04','AEZ_12'], 6.00, 8.00, TRUE, 5650.00),

-- Groundnut
('ARACHIS_HYPOGAEA', 'TG_37A', 'TG 37A', 'Arachis hypogaea L.', '{"hi":"मूंगफली","gu":"મગફળી","te":"వేరుశెనగ"}', 'KHARIF', 100, 120, 500.00, 25.00, 50.00, 40.00, ARRAY['AEZ_07','AEZ_08','AEZ_11'], 5.50, 7.00, TRUE, 6377.00),

-- Pulses
('CICER_ARIETINUM', 'PUSA_256', 'Pusa 256 (Chana)', 'Cicer arietinum L.', '{"hi":"चना पूसा 256","mr":"हरभरा"}', 'RABI', 130, 150, 300.00, 20.00, 40.00, 20.00, ARRAY['AEZ_06','AEZ_07'], 6.00, 8.00, TRUE, 5440.00),
('VIGNA_RADIATA', 'SML_668', 'SML 668 (Moong)', 'Vigna radiata (L.) Wilczek', '{"hi":"मूंग एसएमएल 668","pa":"ਮੂੰਗ"}', 'KHARIF', 55, 70, 250.00, 20.00, 40.00, 20.00, ARRAY['AEZ_03','AEZ_04'], 6.50, 7.50, TRUE, 8558.00),
('CAJANUS_CAJAN', 'ASHA_ICPL_87119', 'Asha (ICPL 87119) Tur', 'Cajanus cajan (L.) Millsp.', '{"hi":"अरहर आशा","mr":"तूर","te":"కందులు"}', 'KHARIF', 160, 190, 600.00, 20.00, 50.00, 20.00, ARRAY['AEZ_06','AEZ_07','AEZ_13'], 6.00, 7.50, TRUE, 7000.00),

-- Vegetables
('SOLANUM_LYCOPERSICUM', 'PUSA_RUBY', 'Pusa Ruby (Tomato)', 'Solanum lycopersicum L.', '{"hi":"टमाटर पूसा रूबी","ta":"தக்காளி"}', 'RABI', 60, 80, 500.00, 120.00, 60.00, 60.00, ARRAY['AEZ_03','AEZ_04','AEZ_07','AEZ_08'], 6.00, 7.00, TRUE, NULL),
('SOLANUM_TUBEROSUM', 'KUFRI_JYOTI', 'Kufri Jyoti (Potato)', 'Solanum tuberosum L.', '{"hi":"आलू कुफरी ज्योति","pa":"ਆਲੂ"}', 'RABI', 90, 120, 500.00, 150.00, 80.00, 100.00, ARRAY['AEZ_01','AEZ_03','AEZ_04'], 5.00, 6.50, TRUE, NULL),
('ALLIUM_CEPA', 'AGRIFOUND_DARK_RED', 'Agrifound Dark Red (Onion)', 'Allium cepa L.', '{"hi":"प्याज","mr":"कांदा","ta":"வெங்காயம்"}', 'RABI', 100, 130, 350.00, 100.00, 50.00, 50.00, ARRAY['AEZ_07','AEZ_08'], 6.00, 7.00, TRUE, NULL),

-- Spices
('CURCUMA_LONGA', 'PRABHA', 'Prabha (Turmeric)', 'Curcuma longa L.', '{"hi":"हल्दी प्रभा","te":"పసుపు","ta":"மஞ்சள்"}', 'KHARIF', 240, 280, 1500.00, 60.00, 30.00, 120.00, ARRAY['AEZ_07','AEZ_08','AEZ_09','AEZ_10'], 5.50, 7.50, TRUE, NULL),
('PIPER_NIGRUM', 'PANNIYUR_1', 'Panniyur-1 (Black Pepper)', 'Piper nigrum L.', '{"ml":"കുരുമുളക്","kn":"ಕಾಳು ಮೆಣಸು"}', 'PERENNIAL', 365, 365, 2500.00, 50.00, 50.00, 150.00, ARRAY['AEZ_09'], 5.50, 6.50, TRUE, NULL)
ON CONFLICT (crop_code, variety_code) DO NOTHING;


-- ────────────────────────────────────────────────────────────
-- 3. PEST & DISEASE KNOWLEDGE BASE (20 major entries)
-- ────────────────────────────────────────────────────────────
INSERT INTO reference.pest_disease (pest_code, common_name, scientific_name, local_names, category, affected_crops, symptoms, management_organic, management_chemical, image_class_label) VALUES
('BLAST_RICE', 'Rice Blast', 'Magnaporthe oryzae', '{"hi":"चावल ब्लास्ट","te":"వరి బ్లాస్ట్"}', 'FUNGAL', ARRAY['ORYZA_SATIVA'], 'Diamond-shaped lesions on leaves with grey center and brown margins. In severe cases, neck rot leads to unfilled grains.', 'Trichoderma viride seed treatment, silicon application, resistant varieties', '[{"active_ingredient":"Tricyclazole 75% WP","dose":"0.6 g/L","waiting_period_days":21},{"active_ingredient":"Isoprothiolane 40% EC","dose":"1.5 mL/L","waiting_period_days":14}]', 'rice_blast'),
('BLIGHT_WHEAT', 'Wheat Leaf Blight', 'Bipolaris sorokiniana', '{"hi":"गेहूं पत्ती झुलसा"}', 'FUNGAL', ARRAY['TRITICUM_AESTIVUM'], 'Oval to elongated dark brown lesions on leaves. Severe infection leads to premature drying of leaves.', 'Crop rotation, resistant varieties, balanced N fertilization', '[{"active_ingredient":"Propiconazole 25% EC","dose":"1 mL/L","waiting_period_days":21}]', 'wheat_leaf_blight'),
('YELLOW_RUST_WHEAT', 'Yellow Rust (Stripe Rust)', 'Puccinia striiformis', '{"hi":"पीला रतुआ","pa":"ਪੀਲੀ ਕੁੰਗੀ"}', 'FUNGAL', ARRAY['TRITICUM_AESTIVUM'], 'Yellow-orange pustules arranged in stripes along leaf veins. Causes significant yield loss in cool, moist conditions.', 'Grow resistant varieties (HD 3086), remove volunteer plants', '[{"active_ingredient":"Propiconazole 25% EC","dose":"1 mL/L","waiting_period_days":21},{"active_ingredient":"Tebuconazole 25.9% EC","dose":"1 mL/L","waiting_period_days":21}]', 'wheat_yellow_rust'),
('FAW', 'Fall Armyworm', 'Spodoptera frugiperda', '{"hi":"सैनिक कीट","mr":"लष्करी अळी","te":"సైనిక పురుగు"}', 'INSECT', ARRAY['ZEA_MAYS','ORYZA_SATIVA'], 'Ragged feeding damage on leaves, windowing pattern. Larvae found in leaf whorl with distinctive inverted Y on head.', 'Trichogramma egg parasitoids, Bacillus thuringiensis spray, push-pull strategy', '[{"active_ingredient":"Emamectin Benzoate 5% SG","dose":"0.4 g/L","waiting_period_days":7},{"active_ingredient":"Spinetoram 11.7% SC","dose":"0.5 mL/L","waiting_period_days":3}]', 'fall_armyworm'),
('BPH', 'Brown Planthopper', 'Nilaparvata lugens', '{"hi":"भूरा फुदका","te":"గోధుమ రంగు తెగులు"}', 'INSECT', ARRAY['ORYZA_SATIVA'], 'Hopperburn — circular patches of dried plants. Honeydew excretion promotes sooty mold. Vector of grassy stunt virus.', 'Drain fields for 3 days, avoid excess nitrogen, encourage spiders', '[{"active_ingredient":"Pymetrozine 50% WG","dose":"0.6 g/L","waiting_period_days":14},{"active_ingredient":"Dinotefuran 20% SG","dose":"0.4 g/L","waiting_period_days":14}]', 'brown_planthopper'),
('LATE_BLIGHT_POTATO', 'Late Blight of Potato', 'Phytophthora infestans', '{"hi":"आलू का पछेती झुलसा"}', 'FUNGAL', ARRAY['SOLANUM_TUBEROSUM','SOLANUM_LYCOPERSICUM'], 'Water-soaked lesions on leaves turning brown-black. White cottony growth on leaf undersurface in humid weather.', 'Bordeaux mixture spray, resistant varieties, destroy infected plant debris', '[{"active_ingredient":"Mancozeb 75% WP","dose":"2.5 g/L","waiting_period_days":7},{"active_ingredient":"Cymoxanil 8% + Mancozeb 64% WP","dose":"3 g/L","waiting_period_days":7}]', 'potato_late_blight'),
('BOLLWORM_PINK', 'Pink Bollworm', 'Pectinophora gossypiella', '{"hi":"गुलाबी सुंडी","gu":"ગુલાબી ઈયળ","te":"గులాబీ పురుగు"}', 'INSECT', ARRAY['GOSSYPIUM'], 'Rosetted or deformed flowers (rosette bloom). Larvae bore into bolls causing lint damage and premature boll opening.', 'Pheromone traps (gossyplure), timely picking of fallen bolls, crop rotation', '[{"active_ingredient":"Profenofos 50% EC","dose":"2 mL/L","waiting_period_days":14}]', 'pink_bollworm'),
('WILT_CHICKPEA', 'Fusarium Wilt of Chickpea', 'Fusarium oxysporum f.sp. ciceris', '{"hi":"चना उकठा","mr":"हरभरा मर"}', 'FUNGAL', ARRAY['CICER_ARIETINUM'], 'Wilting of plants starting from lower leaves. Brownish discoloration of vascular tissue visible on cross-section of stem.', 'Trichoderma harzianum seed treatment, crop rotation with cereals, resistant varieties (JG 63)', '[{"active_ingredient":"Carbendazim 50% WP","dose":"2 g/kg seed (seed treatment)","waiting_period_days":0}]', 'chickpea_fusarium_wilt'),
('LEAF_CURL_TOMATO', 'Tomato Leaf Curl Virus', 'ToLCV (Begomovirus)', '{"hi":"टमाटर पत्ती मोड़ विषाणु","te":"ఆకు ముడత"}', 'VIRAL', ARRAY['SOLANUM_LYCOPERSICUM'], 'Upward curling of leaves, thickening, puckering. Stunted plant growth, reduced fruit set. Transmitted by whitefly.', 'Yellow sticky traps for whitefly, neem oil spray, resistant varieties (Arka Rakshak)', '[{"active_ingredient":"Imidacloprid 17.8% SL","dose":"0.3 mL/L (for whitefly vector)","waiting_period_days":3}]', 'tomato_leaf_curl'),
('STEMB_SUGARCANE', 'Stem Borer of Sugarcane', 'Chilo infuscatellus', '{"hi":"गन्ना तना छेदक","mr":"ऊस खोड किडा"}', 'INSECT', ARRAY['SACCHARUM'], 'Dead hearts in young crop, bore holes in internodes. Reddening of internal tissue. Reduced juice quality.', 'Trichogramma chilonis release, light traps, detrashing of lower leaves', '[{"active_ingredient":"Fipronil 0.3% GR","dose":"25 kg/ha in leaf whorl","waiting_period_days":30}]', 'sugarcane_stem_borer'),
('NITROGEN_DEF', 'Nitrogen Deficiency', NULL, '{"hi":"नाइट्रोजन की कमी","te":"నత్రజని లోపం"}', 'NUTRIENT_DEFICIENCY', ARRAY['ORYZA_SATIVA','TRITICUM_AESTIVUM','ZEA_MAYS','SACCHARUM'], 'General chlorosis starting from older leaves. Leaves turn pale green to yellow. Stunted growth, reduced tillering.', 'Green manure (Sesbania, Dhaincha), FYM application, vermicompost', '[]', 'nitrogen_deficiency'),
('PHOSPHORUS_DEF', 'Phosphorus Deficiency', NULL, '{"hi":"फास्फोरस की कमी"}', 'NUTRIENT_DEFICIENCY', ARRAY['ORYZA_SATIVA','TRITICUM_AESTIVUM','ZEA_MAYS'], 'Dark green to purplish leaves, especially older leaves. Reduced root development, delayed maturity.', 'Bone meal, rock phosphate, PSB (Phosphate Solubilizing Bacteria) inoculation', '[]', 'phosphorus_deficiency'),
('POTASSIUM_DEF', 'Potassium Deficiency', NULL, '{"hi":"पोटाश की कमी"}', 'NUTRIENT_DEFICIENCY', ARRAY['ORYZA_SATIVA','TRITICUM_AESTIVUM','SACCHARUM'], 'Marginal leaf scorch on older leaves, weak stalks prone to lodging. Poor grain filling.', 'Wood ash, banana stem compost, muriate of potash', '[]', 'potassium_deficiency')
ON CONFLICT (pest_code) DO NOTHING;


-- ────────────────────────────────────────────────────────────
-- 4. INPUT PRODUCTS (Fertilizers, Pesticides, Seeds)
-- ────────────────────────────────────────────────────────────
INSERT INTO reference.input_product (product_code, product_name, manufacturer, category, active_ingredient, formulation, unit_of_measure, mrp_inr, is_organic, cib_registration_no) VALUES
-- Fertilizers
('UREA_46N', 'Urea (46% N)', 'IFFCO', 'FERTILIZER', 'Nitrogen 46%', 'Prilled Granular', 'KG', 266.50, FALSE, NULL),
('DAP_18_46', 'Diammonium Phosphate (DAP)', 'IFFCO', 'FERTILIZER', 'N 18% + P2O5 46%', 'Granular', 'KG', 1350.00, FALSE, NULL),
('MOP_60K', 'Muriate of Potash (MOP)', 'IPL', 'FERTILIZER', 'K2O 60%', 'Granular', 'KG', 1700.00, FALSE, NULL),
('NPK_10_26_26', 'NPK 10:26:26', 'IFFCO', 'FERTILIZER', 'N 10% + P2O5 26% + K2O 26%', 'Complex Granular', 'KG', 1470.00, FALSE, NULL),
('SSP_16P', 'Single Super Phosphate (SSP)', 'Paradeep Phosphates', 'FERTILIZER', 'P2O5 16%', 'Granular', 'KG', 550.00, FALSE, NULL),
('ZINC_SULPHATE', 'Zinc Sulphate Heptahydrate 21%', 'Aries Agro', 'FERTILIZER', 'Zn 21%', 'Crystalline', 'KG', 85.00, FALSE, NULL),
('VERMICOMPOST', 'Premium Vermicompost', 'Local FPO', 'FERTILIZER', 'NPK ~ 2:1:1', 'Organic', 'KG', 8.00, TRUE, NULL),
('NEEM_CAKE', 'Neem Cake (Powder)', 'Agri Gold', 'FERTILIZER', 'Azadirachtin-enriched organic', 'Powder', 'KG', 25.00, TRUE, NULL),

-- Pesticides
('EMAMECTIN_5SG', 'Emamectin Benzoate 5% SG', 'Syngenta', 'PESTICIDE', 'Emamectin Benzoate 5%', '5% SG', 'GM', 320.00, FALSE, 'CIR-2018-1234'),
('TRICYCLAZOLE_75WP', 'Tricyclazole 75% WP', 'Dow AgroSciences', 'PESTICIDE', 'Tricyclazole 75%', '75% WP', 'GM', 650.00, FALSE, 'CIR-2015-5678'),
('IMIDACLOPRID_17SL', 'Imidacloprid 17.8% SL', 'Bayer CropScience', 'PESTICIDE', 'Imidacloprid 17.8%', '17.8% SL', 'ML', 450.00, FALSE, 'CIR-2016-9012'),
('MANCOZEB_75WP', 'Mancozeb 75% WP', 'UPL', 'PESTICIDE', 'Mancozeb 75%', '75% WP', 'GM', 280.00, FALSE, 'CIR-2014-3456'),
('NEEM_OIL_1500PPM', 'Neem Oil (1500 ppm Azadirachtin)', 'Multiplex', 'PESTICIDE', 'Azadirachtin 0.15%', 'EC', 'ML', 350.00, TRUE, 'CIR-BIO-2019-789'),

-- Herbicides
('PRETILACHLOR_50EC', 'Pretilachlor 50% EC (Rice Herbicide)', 'Syngenta', 'HERBICIDE', 'Pretilachlor 50%', '50% EC', 'ML', 550.00, FALSE, 'CIR-2017-2345'),
('PENDIMETHALIN_30EC', 'Pendimethalin 30% EC', 'BASF', 'HERBICIDE', 'Pendimethalin 30%', '30% EC', 'ML', 480.00, FALSE, 'CIR-2016-6789'),

-- Biostimulants
('TRICHODERMA_VIR', 'Trichoderma viride (Bio-control)', 'IARI Bio', 'BIOSTIMULANT', 'Trichoderma viride 2x10^9 CFU/g', 'Wettable Powder', 'GM', 120.00, TRUE, 'BIO-2020-001'),
('PSB_BIOFERT', 'PSB Bio-fertilizer', 'IARI Bio', 'BIOSTIMULANT', 'Bacillus megaterium', 'Liquid', 'ML', 95.00, TRUE, 'BIO-2020-002')
ON CONFLICT (product_code) DO NOTHING;


-- ────────────────────────────────────────────────────────────
-- 5. IAM: Default Admin + Demo Farmer User
-- ────────────────────────────────────────────────────────────
INSERT INTO iam."user" (id, phone_number, email, full_name, role, account_status, has_verified_phone, preferred_language, state_code, district_name, farmer_type) VALUES
('a0000000-0000-0000-0000-000000000001', '+919000000001', 'admin@agridecision.ai', 'Platform Admin', 'PLATFORM_ADMIN', 'ACTIVE', TRUE, 'en', 'IN-DL', 'New Delhi', 'SUBSISTENCE'),
('a0000000-0000-0000-0000-000000000002', '+919000000002', 'demo.farmer@agridecision.ai', 'Demo Farmer (Rajesh Kumar)', 'FARMER', 'ACTIVE', TRUE, 'hi', 'IN-UP', 'Lucknow', 'SMALL_COMMERCIAL'),
('a0000000-0000-0000-0000-000000000003', '+919000000003', 'demo.agronomist@agridecision.ai', 'Demo Agronomist (Dr. Priya Sharma)', 'AGRONOMIST', 'ACTIVE', TRUE, 'en', 'IN-MH', 'Pune', 'SUBSISTENCE')
ON CONFLICT (id) DO NOTHING;

-- ────────────────────────────────────────────────────────────
-- VERIFICATION
-- ────────────────────────────────────────────────────────────
DO $$
DECLARE
    aez_count INT; crop_count INT; pest_count INT; input_count INT; user_count INT;
BEGIN
    SELECT count(*) INTO aez_count FROM reference.agro_ecological_zone;
    SELECT count(*) INTO crop_count FROM reference.crop_variety;
    SELECT count(*) INTO pest_count FROM reference.pest_disease;
    SELECT count(*) INTO input_count FROM reference.input_product;
    SELECT count(*) INTO user_count FROM iam."user";
    RAISE NOTICE '══ SEED DATA LOADED ══';
    RAISE NOTICE 'Agro-Ecological Zones: %', aez_count;
    RAISE NOTICE 'Crop Varieties:        %', crop_count;
    RAISE NOTICE 'Pest/Disease Records:  %', pest_count;
    RAISE NOTICE 'Input Products:        %', input_count;
    RAISE NOTICE 'Users:                 %', user_count;
END $$;
