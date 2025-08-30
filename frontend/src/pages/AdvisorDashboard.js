import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
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

const dummyDashboardData = {
  advisor: {
    advisor_name: "John Doe",
    advisor_id: "ADV001",
    department: "Finance",
    business_function: "Wealth Management",
    country: "United States",
    current_advisory_group: "High Net Worth Clients",
    profile_summary: "Experienced financial advisor specializing in wealth management and investment strategies.",
  },
  tags: [
    { tag_name: "Investment" },
    { tag_name: "Retirement Planning" },
    { tag_name: "Tax Optimization" },
    { tag_name: "Portfolio Management" },
    { tag_name: "Risk Assessment" },
  ],
  performance_metrics: {
    success_rate: 85,
    total_cases_handled: 120,
    avg_resolution_time: 3.5,
    pending_cases: 8,
  },
  incoming_cases: [
    {
      case_id: "CASE001",
      topic: "Investment Strategy",
      subtopic: "Stock Market",
      matching_score: 92,
      date_created: "2025-08-25T10:00:00Z",
    },
    {
      case_id: "CASE002",
      topic: "Retirement Planning",
      subtopic: "401(k)",
      matching_score: 88,
      date_created: "2025-08-26T14:30:00Z",
    },
    {
      case_id: "CASE002",
      topic: "Retirement Planning",
      subtopic: "401(k)",
      matching_score: 88,
      date_created: "2025-08-26T14:30:00Z",
    },
    {
      case_id: "CASE003",
      topic: "Retirement Planning",
      subtopic: "401(k)",
      matching_score: 88,
      date_created: "2025-08-26T14:30:00Z",
    },
    {
      case_id: "CASE004",
      topic: "Retirement Planning",
      subtopic: "401(k)",
      matching_score: 88,
      date_created: "2025-08-26T14:30:00Z",
    },
  ],
  resolved_cases: [
    {
      case_id: "CASE003",
      topic: "Tax Optimization",
      subtopic: "Capital Gains",
      resolution_time: 2.5,
      date_resolved: "2025-08-20T09:00:00Z",
    },
    {
      case_id: "CASE004",
      topic: "Portfolio Management",
      subtopic: "Diversification",
      resolution_time: 4.0,
      date_resolved: "2025-08-22T16:00:00Z",
    },
  ],
};

function AdvisorDashboard() {
  const { advisorId } = useParams();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  //commented out first to use dummy data
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await advisorsAPI.getAdvisorDashboard(advisorId || 'ADV001');
        setDashboardData(response.data);
        console.log("data", response.data);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [advisorId]);

  // useEffect(() => {
  //   // Simulate API call delay
  //   const fetchDummyData = async () => {
  //     setLoading(true);
  //     setTimeout(() => {
  //       setDashboardData(dummyDashboardData);
  //       setLoading(false);
  //     }, 1000); // Simulate 1 second delay
  //   };
  
  //   fetchDummyData();
  // }, []);

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

  // Register Chart.js components
  ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);
  
  // Function to calculate average resolution time by month
  const calculateAverageResolutionTime = (resolvedCases) => {
    const monthlyData = {};
  
    resolvedCases.forEach((caseItem) => {
      const month = new Date(caseItem.date_resolved).toLocaleString('default', { month: 'short', year: 'numeric' });
  
      if (!monthlyData[month]) {
        monthlyData[month] = { totalResolutionTime: 0, count: 0 };
      }
  
      monthlyData[month].totalResolutionTime += caseItem.resolution_time;
      monthlyData[month].count += 1;
    });
  
    return Object.keys(monthlyData).map((month) => ({
      month,
      avgResolutionTime: monthlyData[month].totalResolutionTime / monthlyData[month].count,
    }));
  };
  
  const resolvedCasesData = calculateAverageResolutionTime(resolved_cases);
  
  const lineChartData = {
    labels: resolvedCasesData.map((data) => data.month),
    datasets: [
      {
        label: 'Avg Resolution Time (days)',
        data: resolvedCasesData.map((data) => data.avgResolutionTime),
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        tension: 0.4,
      },
    ],
  };
  
  const lineChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Average Resolution Time by Month',
      },
    },
  };
  

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 'bold' }}>
        Advisor Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* Incoming csaes */}
        <Grid item xs={12} md={8}>
        <Card sx={{ height: '400px', display: 'flex', flexDirection: 'column' }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                Pending Cases
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
                    {incoming_cases.length != 0 
                    ? incoming_cases.map((case_item, index) => (
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
                    ))
                  : 
                    (<TableRow>
                    <TableCell colSpan={4}>
                      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100px' }}>
                        <Typography variant="body2" color="text.secondary">
                          No Pending Cases at the moment
                        </Typography>
                      </Box>
                    </TableCell>
                  </TableRow>)}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Advisor Profile */}
        <Grid item xs={12} md={4}>
        <Card sx={{ height: '400px', display: 'flex', flexDirection: 'column' }}>
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

        {/* Resolved Cases */}
        <Grid item xs={12} md={8}>
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

        {/* Chart showing avg days taken to resole */}
        <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                  Average Resolution Time by Month
                </Typography>
                <Line data={lineChartData} options={lineChartOptions} />
              </CardContent>
            </Card>
          </Grid>
      </Grid>
    </Box>
  );
}

export default AdvisorDashboard;

{/* <Grid container spacing={2}>
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
          </Grid> */}