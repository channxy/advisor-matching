import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Avatar,
  Chip,
  Button,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  LinearProgress,
  Rating,
} from '@mui/material';
import {
  Search,
  Person,
  Business,
  LocationOn,
  Schedule,
  Visibility,
} from '@mui/icons-material';
import { advisorsAPI } from '../services/api';

function AdvisorProfiles() {
  const navigate = useNavigate();
  const [advisors, setAdvisors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [departmentFilter, setDepartmentFilter] = useState('');
  const [countryFilter, setCountryFilter] = useState('');

  useEffect(() => {
    fetchAdvisors();
  }, []);

  const fetchAdvisors = async () => {
    try {
      const response = await advisorsAPI.getAdvisors();
      setAdvisors(response.data.advisors);
    } catch (error) {
      console.error('Error fetching advisors:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewProfile = (advisorId) => {
    navigate(`/admin/advisor/${advisorId}`);
  };

  const filteredAdvisors = advisors.filter(advisor => {
    const matchesSearch = advisor.advisor_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         advisor.advisor_id.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesDepartment = !departmentFilter || advisor.department === departmentFilter;
    const matchesCountry = !countryFilter || advisor.country === countryFilter;
    
    return matchesSearch && matchesDepartment && matchesCountry;
  });

  const getUniqueDepartments = () => {
    const departments = [...new Set(advisors.map(a => a.department))];
    return departments.sort();
  };

  const getUniqueCountries = () => {
    const countries = [...new Set(advisors.map(a => a.country))];
    return countries.sort();
  };

  const getPerformanceRating = (successRate) => {
    if (successRate >= 95) return 5;
    if (successRate >= 90) return 4;
    if (successRate >= 80) return 3;
    if (successRate >= 70) return 2;
    return 1;
  };

  const getComplexityLevel = (complexity) => {
    if (complexity >= 80) return 'High';
    if (complexity >= 60) return 'Medium';
    return 'Low';
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 'bold' }}>
        Advisor Profiles
      </Typography>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <TextField
              placeholder="Search advisors..."
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
              <InputLabel>Department</InputLabel>
              <Select
                value={departmentFilter}
                label="Department"
                onChange={(e) => setDepartmentFilter(e.target.value)}
              >
                <MenuItem value="">All</MenuItem>
                {getUniqueDepartments().map(dept => (
                  <MenuItem key={dept} value={dept}>{dept}</MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl sx={{ minWidth: 150 }}>
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
            <Chip
              label={`${filteredAdvisors.length} advisors`}
              color="primary"
              variant="outlined"
            />
          </Box>
        </CardContent>
      </Card>

      {/* Advisor Cards */}
      <Grid container spacing={3}>
        {filteredAdvisors.map((advisor) => (
          <Grid item xs={12} sm={6} md={4} key={advisor.advisor_id}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flexGrow: 1 }}>
                {/* Header */}
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Avatar sx={{ width: 60, height: 60, mr: 2, bgcolor: '#3b82f6' }}>
                    <Person />
                  </Avatar>
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="h6" fontWeight="bold">
                      {advisor.advisor_name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {advisor.advisor_id}
                    </Typography>
                  </Box>
                </Box>

                {/* Department & Location */}
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Business sx={{ mr: 1, fontSize: 16 }} />
                    <Typography variant="body2">
                      {advisor.department} • {advisor.business_function}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <LocationOn sx={{ mr: 1, fontSize: 16 }} />
                    <Typography variant="body2">{advisor.country}</Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {advisor.current_advisory_group}
                  </Typography>
                </Box>

                {/* Performance Metrics */}
                <Box sx={{ mb: 2 }}>
                  <Grid container spacing={1}>
                    <Grid item xs={6}>
                      <Box sx={{ textAlign: 'center', p: 1, backgroundColor: '#f8fafc', borderRadius: 1 }}>
                        <Typography variant="h6" color="success.main" fontWeight="bold">
                          {advisor.success_rate}%
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Success Rate
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box sx={{ textAlign: 'center', p: 1, backgroundColor: '#f8fafc', borderRadius: 1 }}>
                        <Typography variant="h6" color="primary.main" fontWeight="bold">
                          {advisor.total_cases_handled}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Cases Handled
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </Box>

                {/* Performance Rating */}
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Rating
                      value={getPerformanceRating(advisor.success_rate)}
                      readOnly
                      size="small"
                      sx={{ mr: 1 }}
                    />
                    <Typography variant="body2" color="text.secondary">
                      Performance
                    </Typography>
                  </Box>
                </Box>

                {/* Tags */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                    Expertise Level: {getComplexityLevel(advisor.complexity_preference)}
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {advisor.expertise_tags?.split(',').slice(0, 3).map((tag, index) => (
                      <Chip
                        key={index}
                        label={tag.trim()}
                        size="small"
                        variant="outlined"
                        sx={{ fontSize: '0.7rem' }}
                      />
                    ))}
                  </Box>
                </Box>

                {/* Resolution Time */}
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Schedule sx={{ mr: 1, fontSize: 16, color: '#f59e0b' }} />
                    <Typography variant="body2">
                      Avg Resolution: {advisor.avg_resolution_time.toFixed(1)} days
                    </Typography>
                  </Box>
                </Box>

                {/* Action Button */}
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<Visibility />}
                  onClick={() => handleViewProfile(advisor.advisor_id)}
                  sx={{ mt: 'auto' }}
                >
                  View Profile
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {filteredAdvisors.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="h6" color="text.secondary">
            No advisors found matching your criteria
          </Typography>
        </Box>
      )}
    </Box>
  );
}

export default AdvisorProfiles;
