import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Button,
  TextField,
  InputAdornment,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Search,
  Visibility,
  CheckCircle,
  Cancel,
} from '@mui/icons-material';
import { casesAPI, assignmentsAPI } from '../services/api';

function ManageApplications() {
  const navigate = useNavigate();
  const { advisorId } = useParams();
  const [cases, setCases] = useState([]);

  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedCase, setSelectedCase] = useState(null);
  const [actionDialog, setActionDialog] = useState(false);
  const [actionType, setActionType] = useState('');
  const [declineReason, setDeclineReason] = useState('');

  useEffect(() => {
    fetchCases();
  }, []);

  const fetchCases = async () => {
    try {
      const response = await casesAPI.getAdvisorCases(advisorId || 'ADV001', { page: 1, size: 50 });
      setCases(response.data.cases);
    } catch (error) {
      console.error('Error fetching cases:', error);
    }
  };

  const handleViewCase = (caseId) => {
    navigate(`/case/${caseId}`);
  };

  const handleRowClick = (caseId) => {
    handleViewCase(caseId);
  };

  const handleAction = (caseItem, type, event) => {
    event.stopPropagation(); // Prevent row click when clicking action buttons
    setSelectedCase(caseItem);
    setActionType(type);
    setActionDialog(true);
  };

  const handleConfirmAction = async () => {
    if (!selectedCase) return;

    try {
      console.log('Starting action:', actionType);
      console.log('Case ID:', selectedCase.case_id);
      console.log('Advisor ID:', advisorId || 'ADV001');
      
      if (actionType === 'accept') {
        // Accept the case
        console.log('Calling acceptCase API...');
        const response = await assignmentsAPI.acceptCase(selectedCase.case_id, advisorId || 'ADV001');
        console.log('Accept response:', response);
        console.log('Case accepted successfully');
      } else if (actionType === 'decline') {
        // Decline the case
        if (!declineReason.trim()) {
          alert('Please provide a reason for declining the case');
          return;
        }
        console.log('Calling declineCase API...');
        const response = await assignmentsAPI.declineCase(selectedCase.case_id, advisorId || 'ADV001', declineReason);
        console.log('Decline response:', response);
        console.log('Case declined successfully');
      }
      
      setActionDialog(false);
      setSelectedCase(null);
      setActionType('');
      setDeclineReason('');
      fetchCases(); // Refresh the list
    } catch (error) {
      console.error('Error performing action:', error);
      console.error('Error details:', error.response?.data);
      console.error('Error status:', error.response?.status);
      console.error('Error URL:', error.config?.url);
      alert('Failed to perform action: ' + error.message);
    }
  };

  const filteredCases = cases.filter(case_item => {
    const matchesSearch = case_item.case_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         case_item.topic.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         case_item.subtopic.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = !statusFilter || case_item.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

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

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 'bold' }}>
        Manage Cases - {advisorId || 'ADV001'}
      </Typography>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <TextField
              placeholder="Search cases..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
              sx={{ minWidth: 300 }}
            />
            <FormControl sx={{ minWidth: 150 }}>
              <InputLabel>Status</InputLabel>
              <Select
                value={statusFilter}
                label="Status"
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="pending">Pending</MenuItem>
                <MenuItem value="assigned">Assigned</MenuItem>
                <MenuItem value="in_progress">In Progress</MenuItem>
                <MenuItem value="resolved">Resolved</MenuItem>
                <MenuItem value="declined">Declined</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </CardContent>
      </Card>

      {/* Cases Table */}
      <Card>
        <CardContent>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Case ID</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Assignment</TableCell>
                  <TableCell>Match %</TableCell>
                  <TableCell>Topic</TableCell>
                  <TableCell>Subtopic</TableCell>
                  <TableCell>Date Created</TableCell>
                  <TableCell>Age</TableCell>
                  <TableCell>Complexity</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredCases.map((case_item) => (
                  <TableRow 
                    key={case_item.case_id} 
                    hover
                    onClick={() => handleRowClick(case_item.case_id)}
                    sx={{ 
                      cursor: 'pointer',
                      '&:hover': {
                        backgroundColor: 'rgba(59, 130, 246, 0.08)',
                      }
                    }}
                  >
                    <TableCell>
                      <Typography variant="body2" fontWeight="bold">
                        {case_item.case_id}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={getStatusLabel(case_item.status)}
                        color={getStatusColor(case_item.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={case_item.assignment_status || 'N/A'}
                        color={case_item.assignment_status === 'accepted' ? 'success' : 
                               case_item.assignment_status === 'declined' ? 'error' : 
                               case_item.assignment_status === 'pending' ? 'warning' : 'default'}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight="bold">
                        {case_item.matching_score ? `${case_item.matching_score.toFixed(1)}%` : 'N/A'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {case_item.topic}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {case_item.subtopic}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {new Date(case_item.date_created).toLocaleDateString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {Math.floor((new Date() - new Date(case_item.date_created)) / (1000 * 60 * 60 * 24))}d
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={`${case_item.complexity}%`}
                        size="small"
                        variant="outlined"
                        color={case_item.complexity >= 80 ? 'error' : case_item.complexity >= 60 ? 'warning' : 'success'}
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="View Details">
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleViewCase(case_item.case_id);
                            }}
                          >
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                        {case_item.assignment_status === 'pending' && (
                          <>
                            <Tooltip title="Accept Case">
                              <IconButton
                                size="small"
                                color="success"
                                onClick={(e) => handleAction(case_item, 'accept', e)}
                              >
                                <CheckCircle />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Decline Case">
                              <IconButton
                                size="small"
                                color="error"
                                onClick={(e) => handleAction(case_item, 'decline', e)}
                              >
                                <Cancel />
                              </IconButton>
                            </Tooltip>
                          </>
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Action Dialog */}
      <Dialog open={actionDialog} onClose={() => setActionDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {actionType === 'accept' ? 'Accept Case' : 'Decline Case'}
        </DialogTitle>
        <DialogContent>
          {selectedCase && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body1" sx={{ mb: 1 }}>
                <strong>Case ID:</strong> {selectedCase.case_id}
              </Typography>
              <Typography variant="body1" sx={{ mb: 1 }}>
                <strong>Topic:</strong> {selectedCase.topic} - {selectedCase.subtopic}
              </Typography>
              <Typography variant="body1" sx={{ mb: 2 }}>
                <strong>Query:</strong> {selectedCase.query}
              </Typography>
            </Box>
          )}
          
          {actionType === 'decline' && (
            <TextField
              fullWidth
              label="Reason for declining"
              multiline
              rows={3}
              value={declineReason}
              onChange={(e) => setDeclineReason(e.target.value)}
              required
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setActionDialog(false)}>Cancel</Button>
          <Button
            onClick={handleConfirmAction}
            variant="contained"
            color={actionType === 'accept' ? 'success' : 'error'}
            disabled={actionType === 'decline' && !declineReason.trim()}
          >
            {actionType === 'accept' ? 'Accept' : 'Decline'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default ManageApplications;
