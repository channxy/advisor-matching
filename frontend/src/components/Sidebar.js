import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Divider,
  Typography,
  Box,
  Chip,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Assignment as AssignmentIcon,
  People as PeopleIcon,
  Assessment as AssessmentIcon,
  Psychology as PsychologyIcon,
} from '@mui/icons-material';

const drawerWidth = 280;

const menuItems = [
  {
    text: 'Advisor Dashboard',
    icon: <DashboardIcon />,
    path: '/',
    category: 'advisor'
  },
  {
    text: 'Manage Cases',
    icon: <AssignmentIcon />,
    path: '/applications',
    category: 'advisor'
  },
  {
    text: 'All Cases',
    icon: <AssessmentIcon />,
    path: '/admin/cases',
    category: 'admin'
  },
  {
    text: 'Advisor Profiles',
    icon: <PeopleIcon />,
    path: '/admin/advisors',
    category: 'admin'
  },
  {
    text: 'ML Model Performance',
    icon: <PsychologyIcon />,
    path: '/admin/model-performance',
    category: 'admin'
  },
];

function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  
  // Extract advisor ID from current URL or use default
  const getAdvisorId = () => {
    const pathParts = location.pathname.split('/');
    if (pathParts.includes('dashboard') && pathParts[pathParts.indexOf('dashboard') + 1]) {
      return pathParts[pathParts.indexOf('dashboard') + 1];
    }
    if (pathParts.includes('applications') && pathParts[pathParts.indexOf('applications') + 1]) {
      return pathParts[pathParts.indexOf('applications') + 1];
    }
    return 'ADV001'; // Default advisor ID
  };
  
  const advisorId = getAdvisorId();
  
  const handleListItemClick = (index, path) => {
    // Add advisor ID to advisor-specific paths
    if (path === '/applications') {
      navigate(`/applications/${advisorId}`);
    } else if (path === '/') {
      navigate(`/dashboard/${advisorId}`);
    } else {
      navigate(path);
    }
  };

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          backgroundColor: '#1e293b',
          color: 'white',
        },
      }}
    >
      <Box sx={{ p: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 1 }}>
          AdvisorConnect
        </Typography>
        {/* <Chip 
          label="GenAI v2" 
          size="small" 
          sx={{ 
            backgroundColor: '#3b82f6', 
            color: 'white',
            fontSize: '0.75rem'
          }} 
        /> */}
      </Box>
      
      <Divider sx={{ backgroundColor: '#334155' }} />
      
      <Box sx={{ p: 2 }}>
        <Typography variant="overline" sx={{ color: '#94a3b8', fontSize: '0.75rem' }}>
          ADVISOR TOOLS
        </Typography>
      </Box>
      
      <List sx={{ px: 2 }}>
        {menuItems.filter(item => item.category === 'advisor').map((item, index) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={
                (item.path === '/' && location.pathname.startsWith('/dashboard')) ||
                (item.path === '/applications' && location.pathname.startsWith('/applications')) ||
                (item.path !== '/' && item.path !== '/applications' && location.pathname === item.path)
              }
              onClick={() => handleListItemClick(index, item.path)}
              sx={{
                borderRadius: 2,
                mb: 1,
                '&.Mui-selected': {
                  backgroundColor: '#3b82f6',
                  '&:hover': {
                    backgroundColor: '#2563eb',
                  },
                },
                '&:hover': {
                  backgroundColor: '#334155',
                },
              }}
            >
              <ListItemIcon sx={{ color: 'inherit', minWidth: 40 }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      
      <Divider sx={{ backgroundColor: '#334155', my: 2 }} />
      
      <Box sx={{ p: 2 }}>
        <Typography variant="overline" sx={{ color: '#94a3b8', fontSize: '0.75rem' }}>
          ADMIN TOOLS
        </Typography>
      </Box>
      
      <List sx={{ px: 2 }}>
        {menuItems.filter(item => item.category === 'admin').map((item, index) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => handleListItemClick(index + 100, item.path)}
              sx={{
                borderRadius: 2,
                mb: 1,
                '&.Mui-selected': {
                  backgroundColor: '#3b82f6',
                  '&:hover': {
                    backgroundColor: '#2563eb',
                  },
                },
                '&:hover': {
                  backgroundColor: '#334155',
                },
              }}
            >
              <ListItemIcon sx={{ color: 'inherit', minWidth: 40 }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Drawer>
  );
}

export default Sidebar;
