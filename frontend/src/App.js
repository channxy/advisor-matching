import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box } from '@mui/material';

// Components
import Sidebar from './components/Sidebar';
import AdvisorDashboard from './pages/AdvisorDashboard';
import ManageApplications from './pages/ManageApplications';
import CaseDetail from './pages/CaseDetail';
import AdminCases from './pages/AdminCases';
import AdvisorProfiles from './pages/AdvisorProfiles';
import AdvisorDetail from './pages/AdvisorDetail';
import TestCaseDetail from './pages/TestCaseDetail';

const theme = createTheme({
  palette: {
    primary: {
      main: '#3b82f6',
    },
    secondary: {
      main: '#64748b',
    },
    background: {
      default: '#f8fafc',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex' }}>
          <Sidebar />
          <Box
            component="main"
            sx={{
              flexGrow: 1,
              height: '100vh',
              overflow: 'auto',
              backgroundColor: '#f8fafc',
            }}
          >
            <Routes>
              <Route path="/" element={<AdvisorDashboard />} />
              <Route path="/dashboard/:advisorId" element={<AdvisorDashboard />} />
              <Route path="/applications/:advisorId" element={<ManageApplications />} />
              <Route path="/case/:caseId" element={<CaseDetail />} />
              <Route path="/admin/cases" element={<AdminCases />} />
              <Route path="/admin/advisors" element={<AdvisorProfiles />} />
              <Route path="/admin/advisor/:advisorId" element={<AdvisorDetail />} />
              <Route path="/test-case-detail" element={<TestCaseDetail />} />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
