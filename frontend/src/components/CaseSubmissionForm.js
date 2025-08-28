import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Typography,
  Alert,
  LinearProgress,
} from '@mui/material';
import { casesAPI } from '../services/api';

const topics = [
  'Tax Planning',
  'Audit',
  'Strategy',
  'Technology',
  'Risk Management',
  'M&A Advisory',
  'Sustainability Advisory',
  'Forensic Advisory',
  'HR Advisory',
  'Operations Advisory',
];

const subtopics = {
  'Tax Planning': ['Corporate Tax Optimization', 'Personal Tax Planning', 'International Tax', 'Tax Compliance'],
  'Audit': ['Financial Statement Audit', 'Internal Audit', 'Compliance Audit', 'Risk Assessment'],
  'Strategy': ['Business Transformation', 'Market Entry Strategy', 'Digital Strategy', 'Organizational Strategy'],
  'Technology': ['Digital Transformation', 'Cybersecurity Assessment', 'IT Strategy', 'Technology Implementation'],
  'Risk Management': ['Compliance Framework', 'Risk Assessment', 'Regulatory Compliance', 'Operational Risk'],
  'M&A Advisory': ['Due Diligence', 'Valuation', 'Transaction Support', 'Post-Merger Integration'],
  'Sustainability Advisory': ['ESG Reporting', 'Environmental Compliance', 'Sustainability Strategy', 'Carbon Footprint'],
  'Forensic Advisory': ['Fraud Investigation', 'Forensic Accounting', 'Litigation Support', 'Compliance Investigation'],
  'HR Advisory': ['Organizational Development', 'Change Management', 'HR Strategy', 'Talent Management'],
  'Operations Advisory': ['Supply Chain Optimization', 'Process Improvement', 'Operational Efficiency', 'Quality Management'],
};

const countries = [
  'United States',
  'Canada',
  'United Kingdom',
  'Singapore',
  'Australia',
  'Germany',
  'Poland',
  'Mexico',
  'France',
  'Japan',
];

const businessFunctions = [
  'Corporate Tax',
  'Financial Audit',
  'Business Strategy',
  'Digital Transformation',
  'Risk Management',
  'Mergers & Acquisitions',
  'ESG Consulting',
  'Forensic Accounting',
  'HR Consulting',
  'Supply Chain Optimization',
];

function CaseSubmissionForm({ open, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    topic: '',
    subtopic: '',
    query: '',
    casetype: '',
    transaction_type: '',
    business_function: '',
    country: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (field) => (event) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value
    }));
  };

  const handleSubmit = async () => {
    if (!formData.topic || !formData.subtopic || !formData.query) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await casesAPI.submitCase(formData);
      onSuccess(response.data);
      handleClose();
    } catch (error) {
      setError('Failed to submit case. Please try again.');
      console.error('Error submitting case:', error);
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
    });
    setError('');
    setLoading(false);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Typography variant="h6" fontWeight="bold">
          Submit New Case
        </Typography>
      </DialogTitle>
      <DialogContent>
        {loading && <LinearProgress sx={{ mb: 2 }} />}
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth required>
              <InputLabel>Topic</InputLabel>
              <Select
                value={formData.topic}
                label="Topic"
                onChange={handleChange('topic')}
              >
                {topics.map(topic => (
                  <MenuItem key={topic} value={topic}>{topic}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth required>
              <InputLabel>Subtopic</InputLabel>
              <Select
                value={formData.subtopic}
                label="Subtopic"
                onChange={handleChange('subtopic')}
                disabled={!formData.topic}
              >
                {formData.topic && subtopics[formData.topic]?.map(subtopic => (
                  <MenuItem key={subtopic} value={subtopic}>{subtopic}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Query"
              multiline
              rows={4}
              value={formData.query}
              onChange={handleChange('query')}
              required
              placeholder="Describe your case in detail..."
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Case Type"
              value={formData.casetype}
              onChange={handleChange('casetype')}
              placeholder="e.g., Consultation, Audit, Assessment"
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Transaction Type"
              value={formData.transaction_type}
              onChange={handleChange('transaction_type')}
              placeholder="e.g., Planning, Review, Development"
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Business Function</InputLabel>
              <Select
                value={formData.business_function}
                label="Business Function"
                onChange={handleChange('business_function')}
              >
                {businessFunctions.map(func => (
                  <MenuItem key={func} value={func}>{func}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Country</InputLabel>
              <Select
                value={formData.country}
                label="Country"
                onChange={handleChange('country')}
              >
                {countries.map(country => (
                  <MenuItem key={country} value={country}>{country}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={loading || !formData.topic || !formData.subtopic || !formData.query}
        >
          {loading ? 'Submitting...' : 'Submit Case'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default CaseSubmissionForm;
