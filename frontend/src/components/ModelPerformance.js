import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  CircularProgress,
  Alert,
  Box,
  Chip,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Backdrop,
} from '@mui/material';
import {
  Psychology,
  Upload,
  Refresh,
  CheckCircle,
} from '@mui/icons-material';
import { excelAPI } from '../services/api';

const ModelPerformance = () => {
  const [performance, setPerformance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retraining, setRetraining] = useState(false);
  const [retrainDialog, setRetrainDialog] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);

  useEffect(() => {
    fetchModelPerformance();
  }, []);

  const fetchModelPerformance = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await excelAPI.getModelPerformance();
      setPerformance(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch model performance');
    } finally {
      setLoading(false);
    }
  };

  const handleRetrainModel = async () => {
    if (!selectedFile) {
      setError('Please select a file for retraining');
      return;
    }

    try {
      setRetraining(true);
      setError(null);
      
      // Retrain the model
      const retrainResponse = await excelAPI.retrainModel(selectedFile);
      
      if (retrainResponse.data.success) {
        // Show success message briefly
        setError(null);
        
        // Fetch updated model performance data
        await fetchModelPerformance();
        
        // Close dialog and reset
        setRetrainDialog(false);
        setSelectedFile(null);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to retrain model');
    } finally {
      setRetraining(false);
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file && file.name.endsWith('.xlsx')) {
      setSelectedFile(file);
      setError(null);
    } else {
      setError('Please select a valid Excel (.xlsx) file');
    }
  };

  const getAccuracyColor = (score) => {
    if (score >= 0.8) return 'success';
    if (score >= 0.6) return 'warning';
    return 'error';
  };

  const getAccuracyLabel = (score) => {
    if (score >= 0.8) return 'Excellent';
    if (score >= 0.6) return 'Good';
    if (score >= 0.4) return 'Fair';
    return 'Poor';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (error && !performance) {
    return (
      <Alert severity="error" action={
        <Button color="inherit" size="small" onClick={fetchModelPerformance}>
          Retry
        </Button>
      }>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      {/* Full-screen loading backdrop during retraining */}
      <Backdrop
        sx={{ 
          color: '#fff', 
          zIndex: (theme) => theme.zIndex.drawer + 1,
          flexDirection: 'column',
          gap: 2
        }}
        open={retraining}
      >
        <CircularProgress color="inherit" />
        <Typography variant="h6">
          Retraining ML Model...
        </Typography>
        <Typography variant="body2" color="rgba(255,255,255,0.8)">
          This may take a few moments. Please wait.
        </Typography>
      </Backdrop>

      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          <Psychology sx={{ mr: 1, verticalAlign: 'middle' }} />
          ML Model Performance
        </Typography>
        <Button
          variant="contained"
          startIcon={<Refresh />}
          onClick={() => setRetrainDialog(true)}
          disabled={retraining}
        >
          Retrain Model
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {performance && performance.success ? (
        <Grid container spacing={3}>
          {/* Model Overview */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Model Overview
                </Typography>
                <Box display="flex" alignItems="center" mb={2}>
                  <Chip
                    label={performance.model_name}
                    color="primary"
                    icon={<Psychology />}
                  />
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Current model performance metrics
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Test Score */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Test Accuracy
                </Typography>
                <Box display="flex" alignItems="center" mb={1}>
                  <Typography variant="h4" component="span" color={`${getAccuracyColor(performance.test_score)}.main`}>
                    {(performance.test_score * 100).toFixed(1)}%
                  </Typography>
                  <Chip
                    label={getAccuracyLabel(performance.test_score)}
                    color={getAccuracyColor(performance.test_score)}
                    size="small"
                    sx={{ ml: 1 }}
                  />
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={performance.test_score * 100}
                  color={getAccuracyColor(performance.test_score)}
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </CardContent>
            </Card>
          </Grid>

          {/* Training Score */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Training Accuracy
                </Typography>
                <Typography variant="h4" color="primary.main">
                  {(performance.train_score * 100).toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Model performance on training data
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Cross Validation */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Cross-Validation Score
                </Typography>
                <Typography variant="h4" color="secondary.main">
                  {(performance.cv_mean * 100).toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  ±{(performance.cv_std * 100 * 2).toFixed(1)}% (95% confidence)
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Feature Importance */}
          {performance.feature_importance && (
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Feature Importance
                  </Typography>
                  <Grid container spacing={1}>
                    {Object.entries(performance.feature_importance)
                      .sort(([,a], [,b]) => b - a)
                      .map(([feature, importance]) => (
                        <Grid item key={feature}>
                          <Chip
                            label={`${feature}: ${(importance * 100).toFixed(1)}%`}
                            variant="outlined"
                            size="small"
                          />
                        </Grid>
                      ))}
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      ) : (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              No Model Available
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={2}>
              {performance?.message || 'No trained model found. Upload Excel data to train a new model.'}
            </Typography>
            <Button
              variant="contained"
              startIcon={<Upload />}
              onClick={() => setRetrainDialog(true)}
              disabled={retraining}
            >
              Train Model
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Retrain Dialog */}
      <Dialog open={retrainDialog} onClose={() => !retraining && setRetrainDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Retrain ML Model</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" mb={2}>
            Upload new Excel data to retrain the model and improve accuracy.
          </Typography>
          <input
            accept=".xlsx"
            style={{ display: 'none' }}
            id="retrain-file-input"
            type="file"
            onChange={handleFileSelect}
            disabled={retraining}
          />
          <label htmlFor="retrain-file-input">
            <Button
              variant="outlined"
              component="span"
              startIcon={<Upload />}
              fullWidth
              disabled={retraining}
            >
              {selectedFile ? selectedFile.name : 'Select Excel File'}
            </Button>
          </label>
          {selectedFile && (
            <Box mt={1}>
              <Chip
                label={`Selected: ${selectedFile.name}`}
                color="success"
                icon={<CheckCircle />}
                onDelete={() => !retraining && setSelectedFile(null)}
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRetrainDialog(false)} disabled={retraining}>
            Cancel
          </Button>
          <Button
            onClick={handleRetrainModel}
            variant="contained"
            disabled={!selectedFile || retraining}
            startIcon={retraining ? <CircularProgress size={16} /> : <Refresh />}
          >
            {retraining ? 'Retraining...' : 'Retrain Model'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ModelPerformance;
