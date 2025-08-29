import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Grid,
  Typography,
  Box,
  Card,
  CardContent,
  Chip,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { casesAPI, excelAPI } from '../services/api';

function IntegratedCaseSubmission({ open, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    topic: '',
    subtopic: '',
    query: '',
    casetype: '',
    transaction_type: '',
    business_function: '',
    country: '',
    complexity: 50,
  });

  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [step, setStep] = useState(1); // 1: form, 2: recommendations, 3: submission

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleGetRecommendations = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await excelAPI.getRecommendations(formData);
      setRecommendations(response.data.recommendations || []);
      setStep(2);
    } catch (error) {
      setError('Failed to get recommendations: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitCase = async () => {
    setLoading(true);
    setError('');
    
    try {
      // Submit case using the MatchingService endpoint
      const response = await casesAPI.submitCase(formData);
      
      if (response.data) {
        setStep(3);
        onSuccess && onSuccess(response.data);
      }
    } catch (error) {
      setError('Failed to submit case: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setFormData({
      topic: '',
      subtopic: '',
      query: '',
      casetype: '',
      transaction_type: '',
      business_function: '',
      country: '',
      complexity: 50,
    });
    setRecommendations([]);
    setError('');
    setStep(1);
    onClose();
  };

  const renderForm = () => (
    <Grid container spacing={2}>
      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>
          Submit New Case
        </Typography>
        <Typography variant="body2" color="textSecondary" gutterBottom>
          Fill in the case details to get AI-powered advisor recommendations
        </Typography>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Topic"
          value={formData.topic}
          onChange={(e) => handleInputChange('topic', e.target.value)}
          required
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Sub-topic"
          value={formData.subtopic}
          onChange={(e) => handleInputChange('subtopic', e.target.value)}
          required
        />
      </Grid>
      
      <Grid item xs={12}>
        <TextField
          fullWidth
          label="Query Description"
          value={formData.query}
          onChange={(e) => handleInputChange('query', e.target.value)}
          multiline
          rows={3}
          required
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Case Type"
          value={formData.casetype}
          onChange={(e) => handleInputChange('casetype', e.target.value)}
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Transaction Type"
          value={formData.transaction_type}
          onChange={(e) => handleInputChange('transaction_type', e.target.value)}
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Business Function"
          value={formData.business_function}
          onChange={(e) => handleInputChange('business_function', e.target.value)}
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Country"
          value={formData.country}
          onChange={(e) => handleInputChange('country', e.target.value)}
        />
      </Grid>
      
      <Grid item xs={12}>
        <TextField
          fullWidth
          label="Complexity (0-100)"
          type="number"
          value={formData.complexity}
          onChange={(e) => handleInputChange('complexity', parseFloat(e.target.value))}
          inputProps={{ min: 0, max: 100 }}
        />
      </Grid>
    </Grid>
  );

  const renderRecommendations = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        AI Advisor Recommendations
      </Typography>
      <Typography variant="body2" color="textSecondary" gutterBottom>
        Based on your case details, here are the best matching advisors:
      </Typography>
      
      {recommendations.length > 0 ? (
        <Grid container spacing={2}>
          {recommendations.map((rec, index) => (
            <Grid item xs={12} key={index}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Box>
                      <Typography variant="h6">{rec.advisor_name}</Typography>
                      <Typography variant="body2" color="textSecondary">
                        {rec.expertise_tags}
                      </Typography>
                      <Box mt={1}>
                        <Chip 
                          label={`${rec.confidence.toFixed(1)}% Match`} 
                          color="primary" 
                          size="small" 
                        />
                        <Chip 
                          label={`${rec.success_rate.toFixed(1)}% Success Rate`} 
                          color="secondary" 
                          size="small" 
                          sx={{ ml: 1 }}
                        />
                      </Box>
                    </Box>
                    <Typography variant="h4" color="primary">
                      #{index + 1}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      ) : (
        <Alert severity="info">
          No recommendations available. Please check your case details.
        </Alert>
      )}
    </Box>
  );

  const renderSuccess = () => (
    <Box textAlign="center">
      <Typography variant="h6" gutterBottom color="success.main">
        ✅ Case Submitted Successfully!
      </Typography>
      <Typography variant="body2" color="textSecondary">
        Your case has been submitted and assigned to the best matching advisors.
        You can track its progress in the cases dashboard.
      </Typography>
    </Box>
  );

  const renderContent = () => {
    switch (step) {
      case 1:
        return renderForm();
      case 2:
        return renderRecommendations();
      case 3:
        return renderSuccess();
      default:
        return renderForm();
    }
  };

  const renderActions = () => {
    switch (step) {
      case 1:
        return (
          <>
            <Button onClick={handleClose}>Cancel</Button>
            <Button 
              onClick={handleGetRecommendations} 
              variant="contained" 
              disabled={loading || !formData.topic || !formData.subtopic || !formData.query}
            >
              {loading ? <CircularProgress size={20} /> : 'Get Recommendations'}
            </Button>
          </>
        );
      case 2:
        return (
          <>
            <Button onClick={() => setStep(1)}>Back</Button>
            <Button 
              onClick={handleSubmitCase} 
              variant="contained" 
              disabled={loading}
            >
              {loading ? <CircularProgress size={20} /> : 'Submit Case'}
            </Button>
          </>
        );
      case 3:
        return (
          <Button onClick={handleClose} variant="contained">
            Close
          </Button>
        );
      default:
        return <Button onClick={handleClose}>Close</Button>;
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {step === 1 && 'Submit New Case'}
        {step === 2 && 'Advisor Recommendations'}
        {step === 3 && 'Case Submitted'}
      </DialogTitle>
      
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        {renderContent()}
      </DialogContent>
      
      <DialogActions>
        {renderActions()}
      </DialogActions>
    </Dialog>
  );
}

export default IntegratedCaseSubmission;
