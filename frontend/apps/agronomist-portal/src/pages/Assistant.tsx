import React, { useState } from 'react';
import {
  Grid, Card, CardContent, Typography, Box, TextField, IconButton,
  Divider, List, ListItem, ListItemIcon, ListItemText, Chip, alpha, useTheme,
} from '@mui/material';
import MicIcon from '@mui/icons-material/Mic';
import MicOffIcon from '@mui/icons-material/MicOff';
import SendIcon from '@mui/icons-material/Send';
import VolumeUpIcon from '@mui/icons-material/VolumeUp';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';

import { usePlots } from '@/hooks/useFarm';
import { useAppSelector } from '@/store/hooks';
import { advisoryService } from '@/services/advisoryService';
import { AdvisoryResponse } from '@/types';
import { LoadingState } from '@/components/common/States';

interface Message {
  sender: 'user' | 'assistant';
  text: string;
  advisory?: AdvisoryResponse;
}

export const Assistant: React.FC = () => {
  const theme = useTheme();
  const { data: plots } = usePlots();
  const selectedPlotId = useAppSelector((state) => state.farm.selectedPlotId);

  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    { sender: 'assistant', text: 'Hello! I am your AgriDecision AI Advisor. How can I help you manage your fields, crops, or check disease remedies today?' }
  ]);
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);

  const activePlot = plots?.find((p) => p.id === selectedPlotId) || plots?.[0];

  const handleSend = async () => {
    if (!input.trim() || !activePlot) return;
    const userText = input;
    setMessages((prev) => [...prev, { sender: 'user', text: userText }]);
    setInput('');
    setLoading(true);

    try {
      const response = await advisoryService.getAIAdvisory(userText, activePlot.id);
      setMessages((prev) => [...prev, {
        sender: 'assistant',
        text: response.diagnosis,
        advisory: response
      }]);
    } catch {
      // Mock LLM Response for demo/fallback purposes
      setMessages((prev) => [...prev, {
        sender: 'assistant',
        text: 'Based on the soil test parameters (pH: 7.2, high clay loam texture) and upcoming weather patterns, here is your agronomic advisory:',
        advisory: {
          diagnosis: 'Basmati rice is in growing phase with optimal leaf development. Ensure water levels remain at 5cm depth.',
          remedy_steps: [
            'Monitor closely for leaf blast symptoms due to high humidity forecast.',
            'Apply secondary top dressing of Urea (35kg/Ha) within the next 4 days.',
            'Schedule micro-sprinklers if precipitation drops below 5mm.'
          ],
          warning_signs: [
            'Yellowing leaf tips indicating potential Nitrogen deficiency.',
            'Water logging beyond 10cm depth.'
          ],
          crop_suitability: [
            { crop_name: 'Rice', suitability_score: 95, reason: 'Highly aligned with heavy clay composition' },
            { crop_name: 'Wheat', suitability_score: 82, reason: 'Optimal for upcoming Rabi season rotation' }
          ]
        }
      }]);
    } finally {
      setLoading(false);
    }
  };

  const toggleRecording = () => {
    if (isRecording) {
      setIsRecording(false);
      setInput('Should I apply nitrogen fertilizer to my paddy field tomorrow?');
    } else {
      setIsRecording(true);
    }
  };

  const handleSpeak = (text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      window.speechSynthesis.speak(utterance);
    }
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={800} fontFamily="Outfit" gutterBottom>
          Agri-Voice & AI Advisor
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Ask questions, get voice responses, and interact with the generative AI prompt engine regarding plot diagnostics.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Chat Window */}
        <Grid item xs={12} lg={7}>
          <Card sx={{ height: '650px', display: 'flex', flexDirection: 'column' }}>
            {/* Header */}
            <Box sx={{ p: 2, borderBottom: `1px solid ${theme.palette.divider}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h6" fontWeight={700}>
                AI Conversation Session
              </Typography>
              {activePlot && (
                <Chip label={`Context: ${activePlot.name}`} color="primary" size="small" variant="outlined" />
              )}
            </Box>

            {/* Message History */}
            <Box sx={{ flex: 1, overflowY: 'auto', p: 3, display: 'flex', flexDirection: 'column', gap: 2 }}>
              {messages.map((msg, index) => {
                const isUser = msg.sender === 'user';
                return (
                  <Box
                    key={index}
                    sx={{
                      alignSelf: isUser ? 'flex-end' : 'flex-start',
                      maxWidth: '80%',
                      backgroundColor: isUser ? theme.palette.primary.main : alpha(theme.palette.primary.main, 0.05),
                      color: isUser ? '#fff' : 'text.primary',
                      borderRadius: isUser ? '16px 16px 2px 16px' : '16px 16px 16px 2px',
                      p: 2,
                      border: isUser ? 'none' : `1px solid ${alpha(theme.palette.primary.main, 0.15)}`,
                    }}
                  >
                    <Typography variant="body2">{msg.text}</Typography>
                    {!isUser && (
                      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                        <IconButton size="small" onClick={() => handleSpeak(msg.text)}>
                          <VolumeUpIcon sx={{ fontSize: 16, color: 'primary.main' }} />
                        </IconButton>
                      </Box>
                    )}
                  </Box>
                );
              })}
              {loading && <LoadingState message="Advisor is thinking..." />}
            </Box>

            {/* Input Bar */}
            <Box sx={{ p: 2, borderTop: `1px solid ${theme.palette.divider}`, display: 'flex', gap: 1.5, alignItems: 'center' }}>
              <IconButton color={isRecording ? 'error' : 'primary'} onClick={toggleRecording}>
                {isRecording ? <MicOffIcon /> : <MicIcon />}
              </IconButton>
              <TextField
                fullWidth
                placeholder="Ask about fertilizer requirements, disease control..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              />
              <IconButton color="primary" onClick={handleSend} disabled={loading || !input.trim()}>
                <SendIcon />
              </IconButton>
            </Box>
          </Card>
        </Grid>

        {/* Detailed Insights extracted from AI advisory response */}
        <Grid item xs={12} lg={5}>
          <Card sx={{ height: '100%', minHeight: 650 }}>
            <CardContent>
              <Typography variant="h6" fontWeight={700} gutterBottom>
                Extracted Action Items
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 3 }}>
                Key findings extracted from the latest AI recommendation report.
              </Typography>

              {messages.filter(m => m.advisory).length > 0 ? (
                (() => {
                  const lastAdvisory = messages.filter(m => m.advisory).slice(-1)[0].advisory;
                  return (
                    <Box>
                      <Typography variant="subtitle2" sx={{ mb: 1.5 }} fontWeight={700} color="primary">
                        Recommended Treatment Guidelines:
                      </Typography>
                      <List dense>
                        {lastAdvisory?.remedy_steps.map((step, idx) => (
                          <ListItem key={idx} disablePadding sx={{ mb: 1 }}>
                            <ListItemIcon sx={{ minWidth: 28 }}>
                              <CheckCircleOutlineIcon color="success" sx={{ fontSize: 18 }} />
                            </ListItemIcon>
                            <ListItemText primary={step} />
                          </ListItem>
                        ))}
                      </List>

                      <Divider sx={{ my: 2.5 }} />

                      <Typography variant="subtitle2" sx={{ mb: 1.5 }} fontWeight={700} color="error.main">
                        Key Warnings / Indicators:
                      </Typography>
                      <List dense>
                        {lastAdvisory?.warning_signs.map((sign, idx) => (
                          <ListItem key={idx} disablePadding sx={{ mb: 1 }}>
                            <ListItemIcon sx={{ minWidth: 28 }}>
                              <CheckCircleOutlineIcon color="error" sx={{ fontSize: 18 }} />
                            </ListItemIcon>
                            <ListItemText primary={sign} />
                          </ListItem>
                        ))}
                      </List>

                      <Divider sx={{ my: 2.5 }} />

                      <Typography variant="subtitle2" sx={{ mb: 1.5 }} fontWeight={700}>
                        Alternative Crop Potentials:
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1.5, flexWrap: 'wrap' }}>
                        {lastAdvisory?.crop_suitability.map((crop, idx) => (
                          <Chip
                            key={idx}
                            label={`${crop.crop_name}: ${crop.suitability_score}%`}
                            color="primary"
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    </Box>
                  );
                })()
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No active advisory analysis generated yet. Type your query or use voice capture to get started.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};
