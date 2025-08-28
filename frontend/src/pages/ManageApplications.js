import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
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
import { casesAPI } from '../services/api';

function ManageApplications() {
  const navigate = useNavigate();
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
      const response = await casesAPI.getCases({ page: 1, size: 50 });
      setCases(response.data.cases);
    } catch (error) {
      console.error('Error fetching cases:', error);
    }
  };

  const handleViewCase = (caseId) => {
    navigate(`/case/${caseId}`);
  };

  const handleAction = (caseItem, type) => {
    setSelectedCase(caseItem);
    setActionType(type);
    setActionDialog(true);
  };

  const handleConfirmAction = async () => {
    if (!selectedCase) return;

    try {
      if (actionType === 'accept') {
        // Handle accept action
        console.log('Accepting case:', selectedCase.case_id);
      } else if (actionType === 'decline') {
        // Handle decline action
        console.log('Declining case:', selectedCase.case_id, 'Reason:', declineReason);
      }
      
      setActionDialog(false);
      setSelectedCase(null);
      setActionType('');
      setDeclineReason('');
      fetchCases(); // Refresh the list
    } catch (error) {
      console.error('Error performing action:', error);
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
        Manage Applications
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
                  <TableRow key={case_item.case_id} hover>
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
                            onClick={() => handleViewCase(case_item.case_id)}
                          >
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                        {case_item.status === 'pending' && (
                          <>
                            <Tooltip title="Accept Case">
                              <IconButton
                                size="small"
                                color="success"
                                onClick={() => handleAction(case_item, 'accept')}
                              >
                                <CheckCircle />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Decline Case">
                              <IconButton
                                size="small"
                                color="error"
                                onClick={() => handleAction(case_item, 'decline')}
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
