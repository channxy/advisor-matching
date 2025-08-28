import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Grid,
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
  Avatar,
  LinearProgress,
} from '@mui/material';
import {
  TrendingUp,
  Assignment,
  CheckCircle,
  Schedule,
  Person,
  Business,
  LocationOn,
} from '@mui/icons-material';
import { advisorsAPI } from '../services/api';

function AdvisorDashboard() {
  const { advisorId } = useParams();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await advisorsAPI.getAdvisorDashboard(advisorId || 'ADV001');
        setDashboardData(response.data);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [advisorId]);

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
      </Box>
    );
  }

  if (!dashboardData) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h6" color="error">
          Failed to load dashboard data
        </Typography>
      </Box>
    );
  }

  const { advisor, incoming_cases, resolved_cases, performance_metrics, tags } = dashboardData;

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 'bold' }}>
        Advisor Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* Advisor Profile Card */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: 'fit-content' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ width: 60, height: 60, mr: 2, bgcolor: '#3b82f6' }}>
                  <Person />
                </Avatar>
                <Box>
                  <Typography variant="h6" fontWeight="bold">
                    {advisor.advisor_name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {advisor.advisor_id}
                  </Typography>
                </Box>
              </Box>

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
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Assignment sx={{ mr: 1, fontSize: 16 }} />
                  <Typography variant="body2">
                    {advisor.current_advisory_group}
                  </Typography>
                </Box>
              </Box>

              <Typography variant="body2" sx={{ mb: 2 }}>
                {advisor.profile_summary}
              </Typography>

              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                  Expertise Tags
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {tags.slice(0, 5).map((tag, index) => (
                    <Chip
                      key={index}
                      label={tag.tag_name}
                      size="small"
                      variant="outlined"
                      sx={{ fontSize: '0.75rem' }}
                    />
                  ))}
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Metrics */}
        <Grid item xs={12} md={8}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <TrendingUp sx={{ mr: 1, color: '#10b981' }} />
                    <Typography variant="h6" fontWeight="bold">
                      {performance_metrics.success_rate}%
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Success Rate
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Assignment sx={{ mr: 1, color: '#3b82f6' }} />
                    <Typography variant="h6" fontWeight="bold">
                      {performance_metrics.total_cases_handled}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Cases Handled
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Schedule sx={{ mr: 1, color: '#f59e0b' }} />
                    <Typography variant="h6" fontWeight="bold">
                      {performance_metrics.avg_resolution_time.toFixed(1)}d
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Avg Resolution
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <CheckCircle sx={{ mr: 1, color: '#ef4444' }} />
                    <Typography variant="h6" fontWeight="bold">
                      {performance_metrics.pending_cases}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Pending Cases
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>

        {/* Incoming Cases */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                Incoming Cases
              </Typography>
              <TableContainer component={Paper} sx={{ maxHeight: 300 }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Case ID</TableCell>
                      <TableCell>Topic</TableCell>
                      <TableCell>Match %</TableCell>
                      <TableCell>Date</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {incoming_cases.map((case_item, index) => (
                      <TableRow key={index} hover>
                        <TableCell>
                          <Typography variant="body2" fontWeight="bold">
                            {case_item.case_id}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {case_item.topic}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {case_item.subtopic}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={`${case_item.matching_score}%`}
                            size="small"
                            color={case_item.matching_score >= 90 ? 'success' : 'primary'}
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {new Date(case_item.date_created).toLocaleDateString()}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Resolved Cases */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                Recently Resolved
              </Typography>
              <TableContainer component={Paper} sx={{ maxHeight: 300 }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Case ID</TableCell>
                      <TableCell>Topic</TableCell>
                      <TableCell>Resolution</TableCell>
                      <TableCell>Date</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {resolved_cases.map((case_item, index) => (
                      <TableRow key={index} hover>
                        <TableCell>
                          <Typography variant="body2" fontWeight="bold">
                            {case_item.case_id}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {case_item.topic}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {case_item.subtopic}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {case_item.resolution_time?.toFixed(1)}d
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {case_item.date_resolved ? 
                              new Date(case_item.date_resolved).toLocaleDateString() : 
                              'N/A'
                            }
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default AdvisorDashboard;
