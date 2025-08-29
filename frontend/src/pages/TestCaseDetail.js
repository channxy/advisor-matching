import React, { useState, useEffect } from 'react';
import { Box, Typography, Button, Alert, Card, CardContent } from '@mui/material';
import { casesAPI, assignmentsAPI } from '../services/api';

function TestCaseDetail() {
  const [caseData, setCaseData] = useState(null);
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const testCaseDetail = async () => {
    setLoading(true);
    setError('');
    
    try {
      console.log('Testing case detail for CASE001...');
      
      const [caseResponse, assignmentsResponse] = await Promise.all([
        casesAPI.getCase('CASE001'),
        assignmentsAPI.getCaseAssignments('CASE001')
      ]);
      
      console.log('Case response:', caseResponse.data);
      console.log('Assignments response:', assignmentsResponse.data);
      
      setCaseData(caseResponse.data);
      setAssignments(assignmentsResponse.data.assignments || []);
      
    } catch (error) {
      console.error('Error testing case detail:', error);
      setError('Test failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Case Detail Test
      </Typography>
      
      <Button 
        variant="contained" 
        onClick={testCaseDetail}
        disabled={loading}
        sx={{ mb: 3 }}
      >
        {loading ? 'Testing...' : 'Test Case Detail API'}
      </Button>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {caseData && (
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Case Data
            </Typography>
            <pre>{JSON.stringify(caseData, null, 2)}</pre>
          </CardContent>
        </Card>
      )}

      {assignments.length > 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Assignments
            </Typography>
            <pre>{JSON.stringify(assignments, null, 2)}</pre>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}

export default TestCaseDetail;
