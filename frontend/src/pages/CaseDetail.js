import React, { useState, useCallback, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Divider,
  Avatar,
  LinearProgress,
  Alert,
} from '@mui/material';
import {
  ArrowBack,
  CheckCircle,
  Cancel,
  Business,
  LocationOn,
  Schedule,
  Assignment,
  TrendingUp,
} from '@mui/icons-material';
import { casesAPI, assignmentsAPI } from '../services/api';

function CaseDetail() {
  const { caseId } = useParams();
  const navigate = useNavigate();
  const [caseData, setCaseData] = useState(null);
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionDialog, setActionDialog] = useState(false);
  const [actionType, setActionType] = useState('');
  const [declineReason, setDeclineReason] = useState('');

  const fetchCaseData = useCallback(async () => {
    if (!caseId) {
      setError('No case ID provided');
      setLoading(false);
      return;
    }

    try {
      console.log('Fetching case data for:', caseId);
      const [caseResponse, assignmentsResponse] = await Promise.all([
        casesAPI.getCase(caseId),
        assignmentsAPI.getCaseAssignments(caseId)
      ]);
      
      console.log('Case response:', caseResponse.data);
      console.log('Assignments response:', assignmentsResponse.data);
      
      setCaseData(caseResponse.data);
      setAssignments(assignmentsResponse.data.assignments || []);
    } catch (error) {
      console.error('Error fetching case data:', error);
      setError('Failed to load case data: ' + error.message);
    } finally {
      setLoading(false);
    }
  }, [caseId]);

  useEffect(() => {
    fetchCaseData();
  }, [fetchCaseData]);

  const handleAction = (type) => {
    setActionType(type);
    setActionDialog(true);
  };

  const handleConfirmAction = async () => {
    try {
      // Get the advisor ID from the first assignment
      const advisorId = assignments.length > 0 ? assignments[0].advisor_id : 'ADV001';
      
      if (actionType === 'accept') {
        const response = await assignmentsAPI.acceptCase(caseId, advisorId);
        console.log('Case accepted:', response.data);
      } else if (actionType === 'decline') {
        const response = await assignmentsAPI.declineCase(caseId, advisorId, declineReason);
        console.log('Case declined:', response.data);
      }
      
      setActionDialog(false);
      setActionType('');
      setDeclineReason('');
      
      // Refresh case data to show updated status
      await fetchCaseData();
      
    } catch (error) {
      console.error('Error performing action:', error);
      setError('Failed to perform action: ' + error.message);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'warning';
      case 'assigned': return 'info';
      case 'in_progress': return 'primary';
      case 'resolved': return 'success';
      case 'declined': return 'error';
      default: return 'default';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'pending': return 'Pending';
      case 'assigned': return 'Assigned';
      case 'in_progress': return 'In Progress';
      case 'resolved': return 'Resolved';
      case 'declined': return 'Declined';
      default: return status;
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
        <Typography variant="body1" sx={{ mt: 2 }}>
          Loading case details...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          {error}
        </Alert>
        <Button onClick={() => navigate(-1)} sx={{ mt: 2 }}>
          Go Back
        </Button>
      </Box>
    );
  }

  if (!caseData) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          Case not found
        </Alert>
        <Button onClick={() => navigate(-1)} sx={{ mt: 2 }}>
          Go Back
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Button
          startIcon={<ArrowBack />}
          onClick={() => navigate(-1)}
          sx={{ mr: 2 }}
        >
          Back
        </Button>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          Case Details
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Case Information */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
                <Box>
                  <Typography variant="h5" fontWeight="bold" sx={{ mb: 1 }}>
                    {caseData.case_id}
                  </Typography>
                  <Chip
                    label={getStatusLabel(caseData.status)}
                    color={getStatusColor(caseData.status)}
                    sx={{ mb: 2 }}
                  />
                </Box>
                <Box sx={{ textAlign: 'right' }}>
                  <Typography variant="body2" color="text.secondary">
                    Created: {new Date(caseData.date_created).toLocaleDateString()}
                  </Typography>
                  {caseData.date_resolved && (
                    <Typography variant="body2" color="text.secondary">
                      Resolved: {new Date(caseData.date_resolved).toLocaleDateString()}
                    </Typography>
                  )}
                </Box>
              </Box>

              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} sm={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Business sx={{ mr: 1, fontSize: 16 }} />
                    <Typography variant="body2">
                      <strong>Topic:</strong> {caseData.topic}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ ml: 3 }}>
                    {caseData.subtopic}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <LocationOn sx={{ mr: 1, fontSize: 16 }} />
                    <Typography variant="body2">
                      <strong>Country:</strong> {caseData.country || 'N/A'}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ ml: 3 }}>
                    {caseData.business_function || 'N/A'}
                  </Typography>
                </Grid>
              </Grid>

              <Divider sx={{ my: 2 }} />

              <Typography variant="h6" sx={{ mb: 2 }}>
                Query
              </Typography>
              <Typography variant="body1" sx={{ mb: 3, backgroundColor: '#f8fafc', p: 2, borderRadius: 1 }}>
                {caseData.query}
              </Typography>

              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <TrendingUp sx={{ mr: 1, fontSize: 16 }} />
                    <Typography variant="body2">
                      <strong>Complexity:</strong>
                    </Typography>
                  </Box>
                  <Chip
                    label={`${caseData.complexity}%`}
                    color={caseData.complexity >= 80 ? 'error' : caseData.complexity >= 60 ? 'warning' : 'success'}
                    sx={{ ml: 3 }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Schedule sx={{ mr: 1, fontSize: 16 }} />
                    <Typography variant="body2">
                      <strong>Resolution Time:</strong>
                    </Typography>
                  </Box>
                  <Typography variant="body2" sx={{ ml: 3 }}>
                    {caseData.resolution_time ? `${caseData.resolution_time.toFixed(1)} days` : 'N/A'}
                  </Typography>
                </Grid>
              </Grid>

              {caseData.status === 'pending' && (
                <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                  <Button
                    variant="contained"
                    color="success"
                    startIcon={<CheckCircle />}
                    onClick={() => handleAction('accept')}
                  >
                    Accept Case
                  </Button>
                  <Button
                    variant="outlined"
                    color="error"
                    startIcon={<Cancel />}
                    onClick={() => handleAction('decline')}
                  >
                    Decline Case
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Assignments */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                Assignments ({assignments.length})
              </Typography>
              
              {assignments.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  No assignments found
                </Typography>
              ) : (
                assignments.map((assignment, index) => (
                  <Box key={index} sx={{ mb: 2, p: 2, backgroundColor: '#f8fafc', borderRadius: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Avatar sx={{ width: 32, height: 32, mr: 1, bgcolor: '#3b82f6' }}>
                        <Assignment />
                      </Avatar>
                      <Typography variant="body2" fontWeight="bold">
                        {assignment.advisor_name || `Advisor ${assignment.advisor_id}`}
                      </Typography>
                    </Box>
                    <Chip
                      label={`${assignment.matching_score}% match`}
                      size="small"
                      color={assignment.matching_score >= 90 ? 'success' : 'primary'}
                      sx={{ mb: 1 }}
                    />
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                      {assignment.matching_insights}
                    </Typography>
                    {assignment.advisor_expertise && (
                      <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                        <strong>Expertise:</strong> {assignment.advisor_expertise}
                      </Typography>
                    )}
                  </Box>
                ))
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Action Dialog */}
      <Dialog open={actionDialog} onClose={() => setActionDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {actionType === 'accept' ? 'Accept Case' : 'Decline Case'}
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ mb: 2 }}>
            Are you sure you want to {actionType} this case?
          </Typography>
          {actionType === 'decline' && (
            <TextField
              fullWidth
              label="Decline Reason"
              value={declineReason}
              onChange={(e) => setDeclineReason(e.target.value)}
              multiline
              rows={3}
              sx={{ mt: 2 }}
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setActionDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleConfirmAction} 
            variant="contained"
            color={actionType === 'accept' ? 'success' : 'error'}
          >
            {actionType === 'accept' ? 'Accept' : 'Decline'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default CaseDetail;
