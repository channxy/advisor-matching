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
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Tooltip,
  Grid,
  Button,
} from '@mui/material';
import {
  Search,
  Visibility,
  Add,
  Refresh,
  CloudUpload,
} from '@mui/icons-material';
import { casesAPI } from '../services/api';
import IntegratedCaseSubmission from '../components/IntegratedCaseSubmission';
import ExcelUpload from '../components/ExcelUpload';

function AdminCases() {
  const navigate = useNavigate();
  const [cases, setCases] = useState([]);
  const [showCaseSubmission, setShowCaseSubmission] = useState(false);
  const [showExcelUpload, setShowExcelUpload] = useState(false);

  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [topicFilter, setTopicFilter] = useState('');
  const [countryFilter, setCountryFilter] = useState('');

  useEffect(() => {
    fetchCases();
  }, []);

  const fetchCases = async () => {
    try {
      const response = await casesAPI.getCases({ page: 1, size: 100 });
      setCases(response.data.cases);
    } catch (error) {
      console.error('Error fetching cases:', error);
    }
  };

  const handleViewCase = (caseId) => {
    navigate(`/case/${caseId}`);
  };

  const filteredCases = cases.filter(case_item => {
    const matchesSearch = case_item.case_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         case_item.topic.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         case_item.subtopic.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = !statusFilter || case_item.status === statusFilter;
    const matchesTopic = !topicFilter || case_item.topic === topicFilter;
    const matchesCountry = !countryFilter || case_item.country === countryFilter;
    
    return matchesSearch && matchesStatus && matchesTopic && matchesCountry;
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

  const getUniqueTopics = () => {
    const topics = [...new Set(cases.map(c => c.topic))];
    return topics.sort();
  };

  const getUniqueCountries = () => {
    const countries = [...new Set(cases.map(c => c.country).filter(Boolean))];
    return countries.sort();
  };

  const getCaseAge = (dateCreated) => {
    const age = Math.floor((new Date() - new Date(dateCreated)) / (1000 * 60 * 60 * 24));
    return age;
  };

  const getComplexityColor = (complexity) => {
    if (complexity >= 80) return 'error';
    if (complexity >= 60) return 'warning';
    return 'success';
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          All Cases
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={fetchCases}
          >
            Refresh
          </Button>
          <Button
            variant="outlined"
            startIcon={<CloudUpload />}
            onClick={() => setShowExcelUpload(true)}
          >
            Upload Excel
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setShowCaseSubmission(true)}
          >
            New Case
          </Button>
        </Box>
      </Box>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
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
              />
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth>
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
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth>
                <InputLabel>Topic</InputLabel>
                <Select
                  value={topicFilter}
                  label="Topic"
                  onChange={(e) => setTopicFilter(e.target.value)}
                >
                  <MenuItem value="">All</MenuItem>
                  {getUniqueTopics().map(topic => (
                    <MenuItem key={topic} value={topic}>{topic}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth>
                <InputLabel>Country</InputLabel>
                <Select
                  value={countryFilter}
                  label="Country"
                  onChange={(e) => setCountryFilter(e.target.value)}
                >
                  <MenuItem value="">All</MenuItem>
                  {getUniqueCountries().map(country => (
                    <MenuItem key={country} value={country}>{country}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Chip
                  label={`${filteredCases.length} cases`}
                  color="primary"
                  variant="outlined"
                />
                <Chip
                  label={`${cases.filter(c => c.status === 'pending').length} pending`}
                  color="warning"
                  variant="outlined"
                />
                <Chip
                  label={`${cases.filter(c => c.status === 'resolved').length} resolved`}
                  color="success"
                  variant="outlined"
                />
              </Box>
            </Grid>
          </Grid>
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
                  <TableCell>Assigned Advisor</TableCell>
                  <TableCell>Age</TableCell>
                  <TableCell>Country</TableCell>
                  <TableCell>Complexity</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredCases.map((case_item) => (
                  <TableRow 
                    key={case_item.case_id} 
                    hover 
                    onClick={() => handleViewCase(case_item.case_id)}
                    sx={{ cursor: 'pointer' }}
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
                      <Typography variant="body2" color="text.secondary">
                        {case_item.assigned_advisor ? case_item.assigned_advisor.advisor_name : 'Unassigned'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {getCaseAge(case_item.date_created)}d
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {case_item.country || 'N/A'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={`${case_item.complexity}%`}
                        size="small"
                        variant="outlined"
                        color={getComplexityColor(case_item.complexity)}
                      />
                    </TableCell>
                    <TableCell>
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
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Integrated Components */}
      <IntegratedCaseSubmission
        open={showCaseSubmission}
        onClose={() => setShowCaseSubmission(false)}
        onSuccess={(newCase) => {
          setShowCaseSubmission(false);
          fetchCases(); // Refresh the cases list
        }}
      />

      <ExcelUpload
        open={showExcelUpload}
        onClose={() => setShowExcelUpload(false)}
        onSuccess={(result) => {
          setShowExcelUpload(false);
          fetchCases(); // Refresh the cases list
        }}
      />
    </Box>
  );
}

export default AdminCases;
