import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  Grid,
  Chip,
} from '@mui/material';
import { CloudUpload, CheckCircle, Error } from '@mui/icons-material';
import { excelAPI } from '../services/api';

function ExcelUpload({ open, onClose, onSuccess }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState('');

  const handleFileSelect = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile && selectedFile.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') {
      setFile(selectedFile);
      setError('');
    } else {
      setError('Please select a valid Excel (.xlsx) file');
      setFile(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError('');
    setUploadResult(null);

    try {
      const response = await excelAPI.uploadExcel(file);
      setUploadResult(response.data);
      onSuccess && onSuccess(response.data);
    } catch (error) {
      setError('Upload failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setUploading(false);
    }
  };

  const handleClose = () => {
    setFile(null);
    setUploadResult(null);
    setError('');
    onClose();
  };

  const renderUploadForm = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Upload Transaction Data
      </Typography>
      <Typography variant="body2" color="textSecondary" gutterBottom>
        Upload an Excel file with transaction data to generate advisor profiles and train the AI model.
      </Typography>
      
      <Box
        sx={{
          border: '2px dashed #ccc',
          borderRadius: 2,
          p: 3,
          textAlign: 'center',
          mt: 2,
          cursor: 'pointer',
          '&:hover': {
            borderColor: 'primary.main',
          },
        }}
        onClick={() => document.getElementById('file-input').click()}
      >
        <input
          id="file-input"
          type="file"
          accept=".xlsx"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />
        
        {file ? (
          <Box>
            <CheckCircle color="success" sx={{ fontSize: 48, mb: 1 }} />
            <Typography variant="h6" color="success.main">
              File Selected
            </Typography>
            <Typography variant="body2">
              {file.name}
            </Typography>
          </Box>
        ) : (
          <Box>
            <CloudUpload sx={{ fontSize: 48, mb: 1, color: 'text.secondary' }} />
            <Typography variant="h6">
              Click to select Excel file
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Supports .xlsx files with transaction data
            </Typography>
          </Box>
        )}
      </Box>
      
      {file && (
        <Box mt={2}>
          <Typography variant="body2" color="textSecondary">
            Expected columns: Case ID, Services, Topics, Current Sub-Topic, Date Created, 
            Date Submitted, Current Case Owner, Status, Business Function, Country, etc.
          </Typography>
        </Box>
      )}
    </Box>
  );

  const renderUploadResult = () => (
    <Box>
      <Typography variant="h6" gutterBottom color="success.main">
        ✅ Upload Successful!
      </Typography>
      
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Data Processed
              </Typography>
              <Box>
                <Chip 
                  label={`${uploadResult.cases_created} Cases Created`} 
                  color="primary" 
                  sx={{ mr: 1, mb: 1 }}
                />
                <Chip 
                  label={`${uploadResult.advisors_created} Advisors Created`} 
                  color="secondary" 
                  sx={{ mr: 1, mb: 1 }}
                />
                <Chip 
                  label={`${uploadResult.assignments_created} Assignments Created`} 
                  color="info" 
                  sx={{ mb: 1 }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                AI Model Training
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Model Accuracy: {uploadResult.model_accuracy?.toFixed(2) || 'N/A'}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                The AI model has been trained on the new data and is ready for recommendations.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      <Box mt={2}>
        <Typography variant="body2" color="textSecondary">
          The system has successfully processed your Excel data and generated advisor profiles 
          based on historical transaction patterns. You can now use the case submission feature 
          to get AI-powered advisor recommendations.
        </Typography>
      </Box>
    </Box>
  );

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {uploadResult ? 'Upload Complete' : 'Upload Excel Data'}
      </DialogTitle>
      
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        {uploadResult ? renderUploadResult() : renderUploadForm()}
      </DialogContent>
      
      <DialogActions>
        {!uploadResult && (
          <>
            <Button onClick={handleClose}>Cancel</Button>
            <Button 
              onClick={handleUpload} 
              variant="contained" 
              disabled={!file || uploading}
              startIcon={uploading ? <CircularProgress size={20} /> : <CloudUpload />}
            >
              {uploading ? 'Processing...' : 'Upload & Process'}
            </Button>
          </>
        )}
        
        {uploadResult && (
          <Button onClick={handleClose} variant="contained">
            Close
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
}

export default ExcelUpload;
