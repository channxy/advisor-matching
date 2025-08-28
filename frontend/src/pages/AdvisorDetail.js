import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Button,
  Avatar,
  LinearProgress,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
} from '@mui/material';
import {
  ArrowBack,
  Person,
  Business,
  LocationOn,
  Assignment,
  Psychology,
  Timeline,
  Assessment,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { advisorsAPI } from '../services/api';

function AdvisorDetail() {
  const { advisorId } = useParams();
  const navigate = useNavigate();
  const [advisor, setAdvisor] = useState(null);
  const [learningCurve, setLearningCurve] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchAdvisorData = useCallback(async () => {
    try {
      const [advisorResponse, learningCurveResponse] = await Promise.all([
        advisorsAPI.getAdvisor(advisorId),
        advisorsAPI.getLearningCurve(advisorId)
      ]);
      
      setAdvisor(advisorResponse.data);
      setLearningCurve(learningCurveResponse.data.learning_curve || []);
    } catch (error) {
      console.error('Error fetching advisor data:', error);
    } finally {
      setLoading(false);
    }
  }, [advisorId]);

  useEffect(() => {
    fetchAdvisorData();
  }, [fetchAdvisorData]);

  const handleUpdateProfile = async () => {
    try {
      await advisorsAPI.updateProfile(advisorId);
      fetchAdvisorData(); // Refresh data
    } catch (error) {
      console.error('Error updating profile:', error);
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
      </Box>
    );
  }

  if (!advisor) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          Advisor not found
        </Alert>
      </Box>
    );
  }

  const performanceData = [
    { metric: 'Success Rate', value: advisor.success_rate, color: '#10b981' },
    { metric: 'Cases Handled', value: advisor.total_cases_handled, color: '#3b82f6' },
    { metric: 'Avg Resolution', value: advisor.avg_resolution_time, color: '#f59e0b' },
    { metric: 'Complexity Preference', value: advisor.complexity_preference, color: '#8b5cf6' },
  ];

  const expertiseTags = advisor.expertise_tags ? advisor.expertise_tags.split(',').map(tag => tag.trim()) : [];

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
          Advisor Profile
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Advisor Profile Card */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: 'fit-content' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <Avatar sx={{ width: 80, height: 80, mr: 2, bgcolor: '#3b82f6' }}>
                  <Person />
                </Avatar>
                <Box>
                  <Typography variant="h5" fontWeight="bold">
                    {advisor.advisor_name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {advisor.advisor_id}
                  </Typography>
                </Box>
              </Box>

              <Divider sx={{ my: 2 }} />

              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Business sx={{ mr: 1, fontSize: 16 }} />
                  <Typography variant="body2">
                    <strong>Department:</strong> {advisor.department}
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ ml: 3 }}>
                  {advisor.business_function}
                </Typography>
              </Box>

              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <LocationOn sx={{ mr: 1, fontSize: 16 }} />
                  <Typography variant="body2">
                    <strong>Location:</strong> {advisor.country}
                  </Typography>
                </Box>
              </Box>

              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Assignment sx={{ mr: 1, fontSize: 16 }} />
                  <Typography variant="body2">
                    <strong>Current Group:</strong> {advisor.current_advisory_group}
                  </Typography>
                </Box>
                {advisor.previous_advisory_group && (
                  <Typography variant="body2" color="text.secondary" sx={{ ml: 3 }}>
                    Previously: {advisor.previous_advisory_group}
                  </Typography>
                )}
              </Box>

              <Divider sx={{ my: 2 }} />

              <Typography variant="h6" sx={{ mb: 2 }}>
                Profile Summary
              </Typography>
              <Typography variant="body2" sx={{ mb: 2, backgroundColor: '#f8fafc', p: 2, borderRadius: 1 }}>
                {advisor.profile_summary || 'No profile summary available.'}
              </Typography>

              <Typography variant="h6" sx={{ mb: 2 }}>
                Expertise Tags
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
                {expertiseTags.map((tag, index) => (
                  <Chip
                    key={index}
                    label={tag}
                    size="small"
                    variant="outlined"
                    sx={{ fontSize: '0.75rem' }}
                  />
                ))}
              </Box>

              <Button
                variant="contained"
                fullWidth
                onClick={handleUpdateProfile}
                sx={{ mt: 2 }}
              >
                Update Profile
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Metrics */}
        <Grid item xs={12} md={8}>
          <Grid container spacing={2}>
            {performanceData.map((item, index) => (
              <Grid item xs={12} sm={6} key={index}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Box
                        sx={{
                          width: 12,
                          height: 12,
                          borderRadius: '50%',
                          backgroundColor: item.color,
                          mr: 1,
                        }}
                      />
                      <Typography variant="h6" fontWeight="bold">
                        {item.metric === 'Avg Resolution' || item.metric === 'Complexity Preference' 
                          ? `${item.value.toFixed(1)}${item.metric === 'Avg Resolution' ? 'd' : '%'}`
                          : item.metric === 'Cases Handled'
                          ? item.value
                          : `${item.value}%`
                        }
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {item.metric}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Grid>

        {/* Learning Curve Chart */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                Learning Curve - Resolution Time vs Cases Handled
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={learningCurve}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="case_number" />
                  <YAxis />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="avg_resolution_time"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Breakdown */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                Performance Breakdown
              </Typography>
              <TableContainer component={Paper}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Metric</TableCell>
                      <TableCell align="right">Value</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    <TableRow>
                      <TableCell>Total Cases Handled</TableCell>
                      <TableCell align="right">{advisor.total_cases_handled}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Success Rate</TableCell>
                      <TableCell align="right">{advisor.success_rate}%</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Average Resolution Time</TableCell>
                      <TableCell align="right">{advisor.avg_resolution_time.toFixed(1)} days</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Complexity Preference</TableCell>
                      <TableCell align="right">{advisor.complexity_preference}%</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                Recent Activity
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', p: 1, backgroundColor: '#f8fafc', borderRadius: 1 }}>
                  <Timeline sx={{ mr: 1, fontSize: 16, color: '#3b82f6' }} />
                  <Typography variant="body2">
                    Profile last updated: {new Date(advisor.updated_at || advisor.created_at).toLocaleDateString()}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', p: 1, backgroundColor: '#f8fafc', borderRadius: 1 }}>
                  <Assessment sx={{ mr: 1, fontSize: 16, color: '#10b981' }} />
                  <Typography variant="body2">
                    {advisor.total_cases_handled} cases handled successfully
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', p: 1, backgroundColor: '#f8fafc', borderRadius: 1 }}>
                  <Psychology sx={{ mr: 1, fontSize: 16, color: '#f59e0b' }} />
                  <Typography variant="body2">
                    Expertise level: {advisor.complexity_preference >= 80 ? 'High' : advisor.complexity_preference >= 60 ? 'Medium' : 'Low'}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default AdvisorDetail;
