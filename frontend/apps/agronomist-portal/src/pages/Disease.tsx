import React, { useState, useRef } from 'react';
import {
  Grid, Card, CardContent, Typography, Box, Button,
  List, ListItem, ListItemIcon, ListItemText, Alert, Chip, Divider, useTheme,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import BugReportIcon from '@mui/icons-material/BugReport';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import InfoIcon from '@mui/icons-material/Info';
import PhotoLibraryIcon from '@mui/icons-material/PhotoLibrary';

import { advisoryService } from '@/services/advisoryService';
import { DiseaseDetectionResult } from '@/types';
import { LoadingState } from '@/components/common/States';

export const Disease: React.FC = () => {
  const theme = useTheme();
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DiseaseDetectionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setImageFile(file);
      setSelectedImage(URL.createObjectURL(file));
      setResult(null);
      setError(null);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleAnalyze = async () => {
    if (!imageFile) return;
    setLoading(true);
    setError(null);
    try {
      const data = await advisoryService.detectDisease(imageFile);
      setResult(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to detect plant disease. Try uploading a clear leaf image.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={800} fontFamily="Outfit" gutterBottom>
          AI Plant Disease Detection
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Upload a crop leaf photo to analyze diseases, verify diagnostic confidence, and get detailed organic and chemical remedies.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Upload panel */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
              <Typography variant="h6" fontWeight={700} gutterBottom>
                Capture or Upload Leaf Image
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 3 }}>
                Supports JPG, PNG, and JPEG. Make sure the leaf disease lesions are clearly visible.
              </Typography>

              <input
                type="file"
                ref={fileInputRef}
                style={{ display: 'none' }}
                onChange={handleImageChange}
                accept="image/*"
              />

              <Box
                onClick={handleUploadClick}
                sx={{
                  flex: 1,
                  minHeight: 250,
                  border: `2px dashed ${theme.palette.primary.main}`,
                  borderRadius: 2,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  p: 3,
                  backgroundColor: selectedImage ? 'transparent' : 'rgba(46, 125, 50, 0.02)',
                  backgroundImage: selectedImage ? `url(${selectedImage})` : 'none',
                  backgroundSize: 'contain',
                  backgroundPosition: 'center',
                  backgroundRepeat: 'no-repeat',
                  '&:hover': {
                    backgroundColor: 'rgba(46, 125, 50, 0.06)',
                  },
                }}
              >
                {!selectedImage && (
                  <Box sx={{ textAlign: 'center' }}>
                    <CloudUploadIcon sx={{ fontSize: 56, color: 'primary.main', mb: 2 }} />
                    <Typography variant="subtitle1" fontWeight={600}>
                      Drag and drop your file here
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      or click to browse from files
                    </Typography>
                  </Box>
                )}
              </Box>

              {selectedImage && (
                <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
                  <Button variant="outlined" fullWidth onClick={handleUploadClick} startIcon={<PhotoLibraryIcon />}>
                    Change Image
                  </Button>
                  <Button variant="contained" fullWidth onClick={handleAnalyze} disabled={loading} startIcon={<BugReportIcon />}>
                    Run AI Diagnostics
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Diagnostic Results */}
        <Grid item xs={12} md={6}>
          {loading ? (
            <Card sx={{ height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
              <CardContent>
                <LoadingState message="Processing Convolutional Neural Networks (CNN) diagnosis pipelines..." />
              </CardContent>
            </Card>
          ) : error ? (
            <Alert severity="error">{error}</Alert>
          ) : result ? (
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                  <Typography variant="h6" fontWeight={700}>
                    Diagnostics Analysis
                  </Typography>
                  <Chip
                    label={`Confidence: ${(result.confidence_score * 100).toFixed(0)}%`}
                    color={result.confidence_score > 0.8 ? 'success' : 'warning'}
                  />
                </Box>
                <Divider sx={{ mb: 3 }} />

                <Typography variant="h5" fontWeight={800} color="error.main" gutterBottom>
                  {result.predicted_class}
                </Typography>

                <Box sx={{ mb: 4 }}>
                  <Typography variant="subtitle2" sx={{ mb: 1 }} fontWeight={600}>
                    Explainable AI (XAI) Focus Center:
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Grad-CAM activation highlights disease focus coordinates at:
                    <strong> X: {result.focus_attention_center.x}, Y: {result.focus_attention_center.y}</strong>
                  </Typography>
                </Box>

                <Divider sx={{ mb: 3 }} />

                <Typography variant="subtitle1" fontWeight={700} gutterBottom>
                  Recommended Remedies:
                </Typography>
                <List>
                  <ListItem disablePadding sx={{ mb: 1.5 }}>
                    <ListItemIcon>
                      <CheckCircleIcon color="success" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Organic treatment"
                      secondary="Apply neem oil spray solution (2% concentration) early morning to control fungal spore propagation."
                    />
                  </ListItem>
                  <ListItem disablePadding sx={{ mb: 1.5 }}>
                    <ListItemIcon>
                      <CheckCircleIcon color="success" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Chemical treatment (Optional)"
                      secondary="Spray Propiconazole 25% EC (1 ml per Liter water) if severity exceeds 15% threshold limits."
                    />
                  </ListItem>
                  <ListItem disablePadding>
                    <ListItemIcon>
                      <InfoIcon color="info" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Precautionary advice"
                      secondary="Avoid overhead irrigation to minimize leaf moisture retention periods."
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          ) : (
            <Card sx={{ height: '100%', borderStyle: 'dashed', borderWidth: 2, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 350 }}>
              <Box sx={{ textAlign: 'center', opacity: 0.75, p: 3 }}>
                <BugReportIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="text.secondary">
                  Ready for Disease Diagnostics
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1, maxWidth: 300 }}>
                  Upload a crop image and click Run AI Diagnostics to see classifications and explainable heatmaps.
                </Typography>
              </Box>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};
